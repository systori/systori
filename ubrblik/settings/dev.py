from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

STATICFILES_DIRS += (
    ('editor', 'editor/build/web'),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_dev',
    'USER': 'www-data'
})
