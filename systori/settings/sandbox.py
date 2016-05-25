from .common import *

SESSION_COOKIE_SECURE = True                                                    
CSRF_COOKIE_SECURE = True

SERVER_NAME = 'sandbox.systori.com'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME
ALLOWED_HOSTS = ['.'+SERVER_NAME]

STATICFILES_DIRS += (
    ('dart', 'systori/dart/build/web'),
)

DATABASES['default'].update({
    'HOST': 'db',
    'NAME': 'systori_sandbox',
    'USER': 'postgres'
})
