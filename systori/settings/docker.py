import sys
from .dev import *

SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DEBUG = True

DATABASES['default'].update({
    'NAME': 'postgres',
    'USER': 'postgres',
    'HOST': 'db_1',
    'PORT': 5432
})

if 'test' in sys.argv:
    DATABASES['default'].update({
        'NAME': 'systori_travis',
        'TEST': {
            'SERIALIZE': False
        }
    })

INSTALLED_APPS += (
    'django_extensions',
)
