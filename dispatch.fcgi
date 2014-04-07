#!/usr/bin/python2.5

import sys
sys.path += ['/usr/lib/python2.5/site-packages/django']
sys.path += ['/var/www/django_projects/cedir']
sys.path += ['/var/www/django_projects']
from fcgi import WSGIServer
from django.core.handlers.wsgi import WSGIHandler
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'cedir.settings'
WSGIServer(WSGIHandler()).run()