"""
Django settings para ambiente de testes CI/CD
"""

from .base import *

# Database - SQLite para testes locais, PostgreSQL para CI
if os.environ.get('CI') or os.environ.get('DATABASE_HOST'):
    # Configuração para CI/CD com PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DATABASE_NAME', 'test'),
            'USER': os.environ.get('DATABASE_USERNAME', 'postgres'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
            'PORT': os.environ.get('DATABASE_PORT', '5432'),
            'TEST': {
                'NAME': 'test_db',
            }
        }
    }
else:
    # Configuração para testes locais com SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

# Desabilitar migrações para acelerar testes
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Cache simples para testes
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Configurações de performance para testes
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Mock do python-magic se não estiver disponível
try:
    import magic
except ImportError:
    # Criar um mock do módulo magic
    import sys
    from unittest.mock import MagicMock
    
    magic_mock = MagicMock()
    magic_mock.from_buffer.return_value = 'text/plain'
    magic_mock.from_file.return_value = 'text/plain'
    
    sys.modules['magic'] = magic_mock

# Debug desabilitado
DEBUG = False

# Configurações específicas para testes da API
SECRET_KEY = "test-secret-key-not-for-production"
ALLOWED_HOSTS = ['*']

# Configurações para melhorar performance dos testes
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Configurações de media e static para testes
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'test-media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'test-static')

# CRÍTICO: Usar StaticFilesStorage simples em testes (não ManifestStaticFilesStorage)
# ManifestStaticFilesStorage requer collectstatic, que não é executado em testes
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Log simplificado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}