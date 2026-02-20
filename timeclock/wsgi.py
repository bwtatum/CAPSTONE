"""
WSGI Configuration for the TimeClock project.

WSGI (Web Server Gateway Interface) is the traditional synchronous
Python web server interface.

This file is used when deploying with:
- Gunicorn
- uWSGI
- Apache mod_wsgi

The `application` object is the entry point for WSGI servers.
"""

import os
from django.core.wsgi import get_wsgi_application

# Ensure Django uses the correct settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "timeclock.settings")

# WSGI callable exposed for deployment
application = get_wsgi_application()
