"""
Core Application Configuration

Defines the Django app configuration for the core timeclock functionality.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    App configuration for the core timeclock app.

    The name value should match the Django app directory.
    """
    name = "core"
