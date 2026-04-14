#!/usr/bin/env bash
# =============================================================================
# run-pipelines.sh — run inside MSYS2 after file installation
# Prepares example project data by running each project's pipeline.
# Called by the Inno Setup installer with the Windows app directory as $1.
# =============================================================================

# Convert Windows path (e.g. C:\RE2) to MSYS2 path (e.g. /c/RE2)
APPDIR=$(cygpath -u "$1")
SRCDIR="$APPDIR/src"

echo "=== App directory: $APPDIR ==="
echo "=== Src directory: $SRCDIR ==="

run_pipeline() {
    local project="$1"
    local dir="$APPDIR/projects/$project"
    shift
    echo ""
    echo "=== Running $project pipeline ==="
    cd "$dir"
    bash pipeline.sh "$@"
    echo "=== $project pipeline complete ==="
}

# DIS pipeline takes src dir as $1
run_pipeline DIS "$SRCDIR"

# HMONGMIEN pipeline uses hardcoded ../../src/ relative paths; no argument needed
run_pipeline HMONGMIEN

# POLYNESIAN pipeline takes src dir as $1
run_pipeline POLYNESIAN "$SRCDIR"

echo ""
echo "=== All project pipelines complete ==="
