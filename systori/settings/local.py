from .common import *

DEBUG = True
TEMPLATE_DEBUG = True
INSTALLED_APPS += (
    'debug_toolbar',
)

STATICFILES_DIRS += (
    ('editor', os.path.join(ROOT_DIR, 'editor/web')),
    #('editor', os.path.join(ROOT_DIR, 'editor/build/web')),
)

DATABASES['default'].update({
    'NAME': 'systori_local'
})
