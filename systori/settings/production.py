from .common import *
import os

SESSION_COOKIE_SECURE = True                                                    
CSRF_COOKIE_SECURE = True

SERVER_NAME = 'systori.localhost'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME
ALLOWED_HOSTS = ['.'+SERVER_NAME]

STATICFILES_DIRS += (
    ('dart', 'systori/dart/build/web'),
)

DATABASES['default'].update({
    'HOST': 'postgres',
    'NAME': 'systori_production',
    'USER': 'postgres',
    'PASSWORD': os.getenv('POSTGRES_PASSWORD', None),
})

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': 'https://11c0341ce6d74de7968932986090227d:406344d994aa4524818e99d45cf8d44b@sentry.systori.io/1',
}