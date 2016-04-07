from .common import *

SERVER_NAME = 'localhost'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME

GOOGLE_MAPS_API_KEY = "AIzaSyDvwtHHJ_FrNVkbKoHoWh2r2E5PtV5rmLY"

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES['default'].update({
    'NAME': 'systori_travis',
    'TEST': {
        'SERIALIZE': False
    }
})

STATICFILES_DIRS += (
    ('dart', os.path.join(ROOT_DIR, 'systori/dart/build/web')),
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
