from .common import *

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
