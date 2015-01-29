from .common import *

STATICFILES_DIRS += (
    ('editor', '../ubrblik-editor/build/web'),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_production',
    'USER': 'www-data'
})
