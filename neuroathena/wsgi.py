"""
WSGI config for neuroathena project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

# Usar django-dotenv (compatível com o resto do projeto)
try:
    import dotenv
    dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neuroathena.settings.dev")

application = get_wsgi_application()
