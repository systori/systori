from .common import *

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['systori.com']

STATICFILES_DIRS += (
    ('editor', 'editor/build/web'),
)

DATABASES['default'].update({
    'NAME': 'systori_production',
    'USER': 'www-data'
})
