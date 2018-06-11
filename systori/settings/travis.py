from systori.settings.common import *

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SERVER_NAME = 'systori.localhost'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME
ALLOWED_HOSTS = ['.'+SERVER_NAME]

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, 'media'))

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

GOOGLE_MAPS_API_KEY = "AIzaSyDvwtHHJ_FrNVkbKoHoWh2r2E5PtV5rmLY"
