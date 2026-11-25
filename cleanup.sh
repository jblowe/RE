#!/usr/bin/env bash
# cleanup.sh — remove generated run outputs and caches, and reset run state.
#
# Cleans every project directory, wherever it lives:
#   * each directory under projects/ in this repository, and
#   * each directory listed in projects.toml (including ones outside the repo),
#     resolved exactly as the app resolves them (relative to the repo root,
#     ~ and $VARS expanded).
# In each project directory it removes runs/ and __pycache__/ only; lexicons,
# correspondences, MELs and other source files are never touched.
#
# NOTE: runs/ directories outside this repository may be untracked, in which
# case what is removed here cannot be recovered. Use --dry-run to preview.
#
# Usage: ./cleanup.sh [-n|--dry-run]
# Safe to re-run.  Set PYTHON to choose the interpreter (default: python3).

set -e
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
DRY_RUN=0
case "${1:-}" in
    -n|--dry-run) DRY_RUN=1 ;;
    "") ;;
    *) echo "usage: $0 [-n|--dry-run]" >&2; exit 2 ;;
esac

[ "$DRY_RUN" = 1 ] && echo "(dry run: nothing will be removed)"

# remove PATH [PATH...] — delete files/dirs that exist, reporting each one.
remove() {
    local p
    for p in "$@"; do
        if [ -e "$p" ] || [ -L "$p" ]; then
            if [ "$DRY_RUN" = 1 ]; then
                echo "  would remove $p"
            else
                rm -rf -- "$p"
                echo "  removed $p"
            fi
        fi
    done
}

# ── Collect project directories ───────────────────────────────────────────────

# 1. Directories configured in projects.toml (same resolution as src/projects.py).
configured=""
if [ -f projects.toml ]; then
    configured=$("$PYTHON" -c '
import sys
sys.path.insert(0, "src")
import projects
for path in (projects.get_dirs() or {}).values():
    print(path)
')
else
    echo "Warning: projects.toml not found; cleaning only projects/*/" >&2
fi

# 2. Every directory under projects/ in this repository.
local_dirs=$(for d in projects/*/; do [ -d "$d" ] && (cd "$d" && pwd -P); done)

# Union of both, de-duplicated (bash 3.2-safe: no associative arrays).
all_dirs=""
while IFS= read -r d; do
    [ -n "$d" ] || continue
    [ -d "$d" ] && d=$(cd "$d" && pwd -P)
    case "$d" in
        /|"$HOME"|"$HOME"/) echo "Refusing to clean $d" >&2; continue ;;
    esac
    printf '%s\n' "$all_dirs" | grep -Fxq -- "$d" && continue
    all_dirs="${all_dirs:+$all_dirs
}$d"
done <<EOF
$local_dirs
$configured
EOF

# ── Clean each project directory ──────────────────────────────────────────────

echo "=== Cleaning project run outputs ==="
while IFS= read -r d; do
    [ -n "$d" ] || continue
    if [ ! -d "$d" ]; then
        echo "$d  (missing, skipped)"
        continue
    fi
    echo "$d"
    remove "$d/runs" "$d/__pycache__"
done <<EOF
$all_dirs
EOF

# ── Repository-level caches and state ─────────────────────────────────────────

echo "=== Cleaning src / REwww caches ==="
remove src/__pycache__ REwww/__pycache__

echo "=== Resetting run state ==="
remove runs.toml nohup.out

echo "Done."
