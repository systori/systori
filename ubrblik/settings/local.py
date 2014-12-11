from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

STATICFILES_DIRS += (
    ('editor', os.path.join(ROOT_DIR, 'ubrblik-editor/web')),
)
print(STATICFILES_DIRS)

DATABASES['default'].update({
    'NAME': 'django',
    'USER': 'lina',
    'PASSWORD': 'tieb1enck2yaj3ip5by3',
    'HOST': '127.0.0.1',
    'PORT': '5433',
})
