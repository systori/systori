from .common import *

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['systori.com']

STATICFILES_DIRS += (
    ('dart', 'systori/dart/build/web'),
)

DATABASES['default'].update({
    'NAME': 'systori_production',
    'USER': 'www-data'
})
