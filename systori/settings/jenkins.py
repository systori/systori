from .common import *

SERVER_NAME = 'systori.localhost'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME

GOOGLE_MAPS_API_KEY = "AIzaSyDvwtHHJ_FrNVkbKoHoWh2r2E5PtV5rmLY"

DEBUG = True

DATABASES['default'].update({
    'NAME': 'systori_jenkins',
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
