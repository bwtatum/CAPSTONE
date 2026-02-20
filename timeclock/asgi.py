"""
ASGI Configuration for the TimeClock project.

ASGI (Asynchronous Server Gateway Interface) is used when running
Django in async capable environments such as:

- Daphne
- Uvicorn
- Channels
- Future websocket support

Even if not currently using async features, this file is required
for compatibility with modern deployment platforms.

The `application` object is the entry point for ASGI servers.
"""

import os
from django.core.asgi import get_asgi_application

# Ensure Django knows which settings module to use
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "timeclock.settings")

# ASGI callable exposed for deployment
application = get_asgi_application()
