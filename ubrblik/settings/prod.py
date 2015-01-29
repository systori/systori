from .common import *

STATICFILES_DIRS += (
    ('editor', 'ubrblik/static/dart/editor'),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_production',
    'USER': 'www-data'
})
