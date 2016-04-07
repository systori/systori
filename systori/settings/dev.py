from .common import *

SERVER_NAME = 'dev.systori.com'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME

DEBUG = True
TEMPLATE_DEBUG = True

STATICFILES_DIRS += (
    ('dart', 'systori/dart/build/web'),
)

DATABASES['default'].update({
    'NAME': 'systori_dev',
    'USER': 'www-data'
})

# Settings for making Systori all https                                         
SESSION_COOKIE_SECURE = True                                                    
CSRF_COOKIE_SECURE = True
