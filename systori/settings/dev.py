from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '../media'))
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
