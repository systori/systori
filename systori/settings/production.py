from .common import *

SERVER_NAME = 'systori.com'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME

DEBUG = False

ALLOWED_HOSTS = [SERVER_NAME]

STATICFILES_DIRS += (
    ('dart', 'systori/dart/build/web'),
)

DATABASES['default'].update({
    'NAME': 'systori_production',
    'USER': 'www-data'
})
