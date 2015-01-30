from .common import *

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['ubrblik.de']

STATICFILES_DIRS += (
    ('editor', '../ubrblik-editor/build/web'),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_production',
    'USER': 'www-data'
})
