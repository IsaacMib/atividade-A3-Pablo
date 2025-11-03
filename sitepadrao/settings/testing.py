"""
Django settings para ambiente de testes CI/CD
"""

from .base import *

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'test'),
        'USER': os.environ.get('DATABASE_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
        'TEST': {
            'NAME': 'test_ci',
        },
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

# Log mínimo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
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

from .base import *

# Database
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

# Desabilitar cache para testes
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Acelerar testes
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Logging simplificado para testes
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

# Desabilitar migrações desnecessárias durante testes
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Configurações específicas para testes da API
SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = False
ALLOWED_HOSTS = ['*']

# Configurações para melhorar performance dos testes
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Configurações de media e static para testes
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'test-media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'test-static')