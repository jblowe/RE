"""REwww/app.py – Flask web front-end for the Reconstruction Engine.

Usage:
    cd REwww
    python app.py [--host 127.0.0.1] [--port 5001] [--debug]

Modules:
    xslt.py   – XSLT/XML rendering helpers
    routes.py – all HTTP route handlers (registered as a Blueprint)
"""

import os
import sys

from flask import Flask

# ── Path setup ─────────────────────────────────────────────────────────────────
HERE          = os.path.dirname(os.path.abspath(__file__))
SRC_DIR       = os.path.join(HERE, '..', 'src')
STYLES_DIR    = os.path.join(HERE, '..', 'styles')
STATIC_DIR    = os.path.join(HERE, 'static')
PROJECTS_TOML = os.path.normpath(os.path.join(HERE, '..', 'projects.toml'))
RUNLOG_PATH   = os.path.normpath(os.path.join(HERE, '..', 'runs.toml'))

sys.path.insert(0, SRC_DIR)

# Wire shared config into sub-modules before importing them
import xslt
xslt.STYLES_DIR = os.path.normpath(STYLES_DIR)

import runlog
runlog.RUNLOG_PATH = RUNLOG_PATH

import routes
routes.PROJECTS_TOML = PROJECTS_TOML

# ── Flask app ──────────────────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=os.path.join(HERE, 'templates'),
    static_folder=STATIC_DIR,
    static_url_path='/static',
)
app.register_blueprint(routes.bp)

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='RE Flask web app')
    parser.add_argument('--host',  default='127.0.0.1')
    parser.add_argument('--port',  type=int, default=3001)
    parser.add_argument('--debug', action='store_true')
    a = parser.parse_args()
    app.run(host=a.host, port=a.port, debug=a.debug)
