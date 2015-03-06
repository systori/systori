from .common import *

DEBUG = True
TEMPLATE_DEBUG = True
INSTALLED_APPS += (
    'debug_toolbar',
)

STATICFILES_DIRS += (
    ('editor', os.path.join(ROOT_DIR, 'editor/web')),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_local'
})
