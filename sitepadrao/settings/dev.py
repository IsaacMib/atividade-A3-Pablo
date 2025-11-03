from .base import *  # noqa: F403, F401
from decouple import config

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-se&)zrfyqgaz=ogd4r-ad!73@lw!^h#1ldl8cuwl^#@6@p&ox*"

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Permite iframes para documentos (desenvolvimento)
X_FRAME_OPTIONS = 'SAMEORIGIN'

# WAGTAILADMIN_BASE_URL required for notification emails
WAGTAILADMIN_BASE_URL = config('WAGTAILADMIN_BASE_URL', default="http://localhost:8000")

try:
    from .local import *  # noqa
except ImportError:
    pass