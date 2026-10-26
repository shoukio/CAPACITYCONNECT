"""Local development settings."""

from .base import *


SECRET_KEY = SECRET_KEY or "django-insecure-local-development-only-change-me"
DEBUG = env.bool("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost"],
)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
