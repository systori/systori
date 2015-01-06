from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

STATICFILES_DIRS += (
    ('editor', os.path.join(PROJECTS_DIR, 'ubrblik-editor/web')),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_local'
})
