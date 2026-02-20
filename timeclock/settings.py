"""
Django Settings for TimeClock Project.

This file defines:

- Application configuration
- Database settings
- Middleware stack
- Template behavior
- Authentication behavior
- Static file handling

Current Environment:
- Development mode (DEBUG = True)
- SQLite database
- Single Django app: core

IMPORTANT:
Do not use DEBUG=True in production.
Move SECRET_KEY and other sensitive values to environment variables
before deploying publicly.
"""

from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------
# SECURITY SETTINGS
# ---------------------------------------------------------------------

# WARNING: Move this to environment variables in production
SECRET_KEY = "django-insecure-REPLACE-IN-PRODUCTION"

# Debug mode should be False in production
DEBUG = True

# Hosts allowed to access the application
ALLOWED_HOSTS = []


# ---------------------------------------------------------------------
# APPLICATION DEFINITION
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Core TimeClock application
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "timeclock.urls"


# ---------------------------------------------------------------------
# TEMPLATE CONFIGURATION
# ---------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Can add custom global templates directory here if needed
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "timeclock.wsgi.application"


# ---------------------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------------------

"""
Currently using SQLite for development.

File location:
BASE_DIR / db.sqlite3

For production, consider:
- PostgreSQL
- MySQL
- Separate database server
"""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ---------------------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

# Consider changing to your local timezone for accurate reporting
TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------

STATIC_URL = "static/"


# ---------------------------------------------------------------------
# AUTHENTICATION REDIRECTS
# ---------------------------------------------------------------------

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"
