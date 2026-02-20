"""
Root URL Configuration for TimeClock.

This file defines the top level routing of the application.

Routing structure:

/admin/       → Django admin site
/accounts/    → Django built-in authentication views
/             → Core timeclock application

The core app handles:
- Landing page
- Dashboard
- Clock in and clock out
- Admin portal
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin interface
    path("admin/", admin.site.urls),

    # Built-in authentication views (login, logout, password reset)
    path("accounts/", include("django.contrib.auth.urls")),

    # Core application routes
    path("", include("core.urls")),
]
