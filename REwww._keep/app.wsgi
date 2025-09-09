import sys
import os

sys.path.insert(0, '/home/ubuntu/RE/REwww')
os.chdir('/home/ubuntu/RE/REwww')

from bottle import default_app
import app  # registers your routes

application = default_app()

