"""REwww/runlog.py – Persistent run log stored in runs.toml."""

import os

try:
    import tomllib                  # stdlib Python ≥ 3.11
except ImportError:
    import tomli as tomllib         # fallback: pip install tomli

import tomli_w                      # pip install tomli-w

# Set by app.py after import
RUNLOG_PATH: str = ''


def _read() -> list:
    if not RUNLOG_PATH or not os.path.isfile(RUNLOG_PATH):
        return []
    with open(RUNLOG_PATH, 'rb') as fh:
        return tomllib.load(fh).get('runs', [])


def _write(runs: list) -> None:
    with open(RUNLOG_PATH, 'wb') as fh:
        tomli_w.dump({'runs': runs}, fh)


def append_run(record: dict) -> None:
    """Append one completed-run record to runs.toml (read-modify-write)."""
    runs = _read()
    runs.append(record)
    _write(runs)


def get_runs(project: str | None = None) -> list:
    """Return all run records newest-first; optionally filtered by project."""
    runs = _read()
    if project:
        runs = [r for r in runs if r.get('project') == project]
    return list(reversed(runs))


def get_run(run_id: str) -> dict | None:
    """Return the record for a specific run_id, or None."""
    for r in _read():
        if r.get('run_id') == run_id:
            return r
    return None


def count_runs(project: str) -> int:
    """Return the number of logged runs for a project."""
    return sum(1 for r in _read() if r.get('project') == project)


def delete_run(run_id: str) -> dict | None:
    """Remove a run record from the log; return the removed record or None."""
    runs = _read()
    for i, r in enumerate(runs):
        if r.get('run_id') == run_id:
            removed = runs.pop(i)
            _write(runs)
            return removed
    return None
