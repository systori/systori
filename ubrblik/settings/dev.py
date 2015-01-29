from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

STATICFILES_DIRS += (
    ('editor', 'ubrblik/static/dart/editor'),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_dev',
    'USER': 'www-data'
})
