"""pytest configuration and shared fixtures for the RE2 test suite.

Adds src/ and REwww/ to sys.path so that modules can be imported without
installation.  The Flask app is constructed once per session; each test
gets its own isolated run log via a tmp_path-backed RUNLOG_PATH.
"""

import os
import sys
import pytest

# ── Resolve repo root regardless of where pytest is invoked from ───────────────
REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

# Insert at position 0 so repo copies take priority over any installed versions.
sys.path.insert(0, os.path.join(REPO, 'src'))
sys.path.insert(0, os.path.join(REPO, 'REwww'))

# ── Bootstrap the Flask app ────────────────────────────────────────────────────
# app.py self-configures STYLES_DIR, PROJECTS_TOML, and RUNLOG_PATH using
# its own __file__ location (REwww/), so those paths are correct without
# any extra configuration here.
from app import app as _flask_app   # noqa: E402  (must come after sys.path setup)
import runlog as _runlog             # noqa: E402

_flask_app.config['TESTING'] = True


# ── Marker registration ────────────────────────────────────────────────────────
def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'slow: marks tests that run a full RE reconstruction (may take minutes)',
    )


# ── Session-scoped app ─────────────────────────────────────────────────────────
@pytest.fixture(scope='session')
def app():
    """Return the Flask application (shared across the whole test session)."""
    return _flask_app


# ── Function-scoped test client with isolated run log ─────────────────────────
@pytest.fixture
def client(app, tmp_path):
    """Flask test client whose run log is redirected to a temporary file.

    This prevents tests from polluting (or depending on) the real runs.toml.
    """
    original_path = _runlog.RUNLOG_PATH
    _runlog.RUNLOG_PATH = str(tmp_path / 'runs.toml')
    with app.test_client() as c:
        yield c
    _runlog.RUNLOG_PATH = original_path


# ── Convenience constants exposed to test modules ──────────────────────────────
@pytest.fixture(scope='session')
def repo_root():
    return REPO
