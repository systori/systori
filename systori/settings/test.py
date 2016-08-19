from .common import *

SERVER_NAME = 'systori.localhost'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME

GOOGLE_MAPS_API_KEY = "AIzaSyDvwtHHJ_FrNVkbKoHoWh2r2E5PtV5rmLY"

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DEBUG = True

DATABASES['default'].update({
    'NAME': 'systori_test',
    'USER': 'postgres',
    'HOST': 'db',
    'PORT': 5432,
    'TEST': {
        'SERIALIZE': False
    }
})

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
