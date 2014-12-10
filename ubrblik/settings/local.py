from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

STATICFILES_DIRS += (
    ('editor', os.path.join(ROOT_DIR, 'ubrblik-editor/web')),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_local',
})
