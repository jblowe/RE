import os
# Ensure subprocesses spawned by the app (pipeline scripts, xsltproc.py, etc.)
# find the venv's python3 rather than the system one.
os.environ['PATH'] = '/home/ubuntu/venv/bin:' + os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')
# mod_wsgi spawns this process (WSGIDaemonProcess ... user=ubuntu) without a
# guaranteed login environment, so $HOME may not resolve to /home/ubuntu even
# though the process runs as that user -- NLTK's default "~/nltk_data" lookup
# would then miss the corpora (stopwords, wordnet) that mel.py needs. Point
# it at the fixed path explicitly rather than relying on HOME.
os.environ.setdefault('NLTK_DATA', '/home/ubuntu/nltk_data')

import sys
sys.path.insert(0, '/home/ubuntu/RE/REwww')
from app import app as application
