"""Production settings with deployment safety checks."""

from django.core.exceptions import ImproperlyConfigured

from .base import *


DEBUG = False

if not SECRET_KEY:
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY in the production environment.")

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Set DJANGO_ALLOWED_HOSTS to your production hostnames."
    )

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
