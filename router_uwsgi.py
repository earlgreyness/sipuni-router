import sys
import os

APP_PATH = '/home/router'
sys.path.insert(0, APP_PATH)
os.chdir(APP_PATH)

from router import app as application
