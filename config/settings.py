"""
Django settings for hexa.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import logging.config
import os
from pathlib import Path

from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: keep the encryption key used in production secret!
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "false") == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Application definition
INSTALLED_APPS = [
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_countries",
    "django_ltree",
    "ariadne_django",
    "tailwind",
    "dpq",
    "hexa.user_management",
    "hexa.metrics",
    "hexa.core",
    "hexa.catalog",
    "hexa.countries",
    "hexa.visualizations",
    "hexa.notebooks",
    "hexa.pipelines",
    "hexa.comments",
    "hexa.tags",
    "hexa.ui",
    "hexa.plugins.connector_dhis2",
    "hexa.plugins.connector_s3",
    "hexa.plugins.connector_gcs",
    "hexa.plugins.connector_airflow",
    "hexa.plugins.connector_postgresql",
    "hexa.plugins.connector_accessmod",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "hexa.plugins.connector_airflow.middlewares.dag_run_authentication_middleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "hexa.user_management.middlewares.login_required_middleware",
    "hexa.user_management.middlewares.accepted_tos_required_middleware",
    "hexa.metrics.middlewares.track_request_event",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "hexa" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "hexa.core.context_processors.global_variables",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
    }
}

# Auth settings
LOGIN_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Custom user model
# https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = "user_management.User"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Authentication backends
# https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "hexa.user_management.backends.PermissionsBackend",
]

# Additional security settings
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true") != "false"
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "true") != "false"
SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN", None)
SECURE_HSTS_SECONDS = os.environ.get(
    "SECURE_HSTS_SECONDS", 60 * 60
)  # TODO: increase to one year if ok
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true") != "false"
SECURE_REDIRECT_EXEMPT = [r"^ready$"]

# by default users need to login every 2 weeks -> update to 1 year
SESSION_COOKIE_AGE = 365 * 24 * 3600

# Trust the X_FORWARDED_PROTO header from the GCP load balancer so Django is aware it is accessed by https
if "TRUST_FORWARDED_PROTO" in os.environ:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# GraphQL
ENABLE_GRAPHQL = os.environ.get("ENABLE_GRAPHQL", "false") == "true"

# CORS (For GraphQL)
# https://github.com/adamchainz/django-cors-headers

RAW_CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS")
if RAW_CORS_ALLOWED_ORIGINS is not None:
    CORS_ALLOWED_ORIGINS = RAW_CORS_ALLOWED_ORIGINS.split(",")
    CORS_URLS_REGEX = r"^/graphql/$"
    CORS_ALLOW_CREDENTIALS = True


CORS_ALLOW_HEADERS = list(default_headers) + [
    "sentry-trace",
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "hexa" / "static"]

# Whitenoise
# http://whitenoise.evans.io/en/stable/django.html#add-compression-and-caching-support
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Comments
COMMENTS_APP = "hexa.comments"

# Tailwind
TAILWIND_APP_NAME = "hexa.ui"

# Notebooks component
NOTEBOOKS_URL = os.environ.get("NOTEBOOKS_URL", "http://localhost:8001")

GRAPHQL_DEFAULT_PAGE_SIZE = 10
GRAPHQL_MAX_PAGE_SIZE = 10_000

# Activate the accept terms of service feature: each user need to manualy accept
# them once if they want to continue using the product, existing user and new one
USER_MUST_ACCEPT_TOS = os.environ.get("USER_MUST_ACCEPT_TOS") == "true"

SENTRY_DSN = os.environ.get("SENTRY_DSN")

if SENTRY_DSN:
    # if sentry -> we are in production, use fluentd handlers
    # inject sentry into logger config afterward.
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {},
        "handlers": {
            "fluentd": {"level": "INFO", "class": "config.logging.GCPHandler"},
        },
        "loggers": {
            "django.security.DisallowedHost": {
                "level": "CRITICAL",
                "propagate": True,
            },
            "django": {
                "level": "INFO",
                "propagate": True,
            },
            "gunicorn": {
                "level": "INFO",
                "propagate": True,
            },
            "": {
                "handlers": ["fluentd"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

    # Ignore "Invalid HTTP_HOST header" errors
    # as crawlers/bots hit the production hundreds of times per day
    # with the IP instead of the host
    ignore_logger("django.security.DisallowedHost")

    # inject sentry into logging config. set level to ERROR, we don't really want the rest?
    sentry_logging = LoggingIntegration(level=logging.ERROR, event_level=logging.ERROR)

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), sentry_logging],
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "1")),
        send_default_pii=True,
        environment=os.environ.get("SENTRY_ENVIRONMENT"),
    )
elif os.environ.get("DEBUG_LOGGING", "false") == "true":
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    }

# Email settings
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS") == "true"
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "OpenHexa <hexatron@notifications.openhexa.org>"
)

if all([EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Sync settings: sync datasource with a worker (good for scaling) or in the web serv (good for dev)
EXTERNAL_ASYNC_REFRESH = os.environ.get("EXTERNAL_ASYNC_REFRESH") == "true"

# Activate an analytics middleware to save every call done on the app
SAVE_REQUESTS = os.environ.get("SAVE_REQUESTS") == "true"

if os.environ.get("DEBUG_TOOLBAR", "false") == "true":
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    # Django Tailwind and Django Debug Toolbar specifically ask for INTERNAL_IPS to be set
    # https://django-tailwind.readthedocs.io/en/latest/installation.html
    # > Make sure that the INTERNAL_IPS list is present in the settings.py
    # > file and contains the 127.0.0.1 ip address
    INTERNAL_IPS = ["127.0.0.1"]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: request.user.is_staff,
    }

if os.environ.get("STORAGE", "local") == "google-cloud":
    # activate google cloud storage, used for dashboard screenshot, ...
    # user generated content
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_BUCKET_NAME = os.environ.get("STORAGE_BUCKET")
    GS_FILE_OVERWRITE = False
else:
    MEDIA_ROOT = BASE_DIR / "static" / "uploads"

# Accessmod settings
ACCESSMOD_BUCKET_NAME = os.environ.get("ACCESSMOD_BUCKET_NAME")
ACCESSMOD_MANAGE_REQUESTS_URL = os.environ.get("ACCESSMOD_MANAGE_REQUESTS_URL")
ACCESSMOD_SET_PASSWORD_URL = os.environ.get("ACCESSMOD_SET_PASSWORD_URL")

# Custom test runner
TEST_RUNNER = "hexa.core.test.runner.DiscoverRunner"

# Specific settings for airflow plugins

# number of second of airflow dag reloading setting
AIRFLOW_SYNC_WAIT = 61

GCS_TOKEN_LIFETIME = os.environ.get("GCS_TOKEN_LIFETIME")

# Needed so that external component know how to hit us back
# Do not add a trailing slash
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
