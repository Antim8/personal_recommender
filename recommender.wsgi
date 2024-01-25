import sys

import os
sys.path.insert(1, '/home/user137/public_html/personal_recommender')
os.chdir('/home/user137/public_html/personal_recommender')

from recommender import app
application = app
