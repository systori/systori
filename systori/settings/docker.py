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

INSTALLED_APPS += (
    'django_extensions',
)
