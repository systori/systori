from .common import *

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['systori.com']

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '../media'))
STATICFILES_DIRS += (
    ('dart', 'systori/dart/build/web'),
)

DATABASES['default'].update({
    'NAME': 'systori_production',
    'USER': 'www-data'
})
