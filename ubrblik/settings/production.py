from .common import *

DEBUG = False
TEMPLATE_DEBUG = False

STATICFILES_DIRS += (
    ('editor', '../ubrblik-editor/build/web'),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_production',
    'USER': 'www-data'
})
