import sys
from .common import *

SERVER_NAME = 'systori.localhost'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DEBUG = True

DATABASES['default'].update({
    'NAME': 'postgres',
    'USER': 'postgres',
    'HOST': 'db',
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

STATICFILES_DIRS += (
     ('dart', os.path.join(ROOT_DIR, 'systori/dart/web')),
    #('dart', os.path.join(ROOT_DIR, 'systori/dart/build/web')),
)
