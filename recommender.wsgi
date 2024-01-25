import sys

import os
sys.path.insert(1, '/home/user137/public_html/search_engine')
os.chdir('/home/user137/public_html/search_engine')

from search import app
application = app
