#!/usr/bin/env bash
# cleanup.sh — remove all generated / .gitignored files and reset run state.
# Safe to re-run; source data, correspondences, and reference inputs are untouched.

set -e
cd "$(dirname "$0")"

echo "=== Cleaning project run outputs ==="
rm -rf projects/*/runs/

# Python caches in project directories
rm -rf projects/*/__pycache__

echo "=== Cleaning src / REwww caches ==="
rm -rf src/__pycache__
rm -rf REwww/__pycache__

echo "=== Resetting run state ==="
rm -f runs.toml
rm -f nohup.out

echo "Done."
