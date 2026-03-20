import os
# Ensure subprocesses spawned by the app (pipeline scripts, xsltproc.py, etc.)
# find the venv's python3 rather than the system one.
os.environ['PATH'] = '/home/ubuntu/venv/bin:' + os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')

import sys
sys.path.insert(0, '/home/ubuntu/RE/REwww')
from app import app as application
