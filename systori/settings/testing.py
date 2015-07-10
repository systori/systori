from .common import *

GOOGLE_MAPS_API_KEY = "AIzaSyDvwtHHJ_FrNVkbKoHoWh2r2E5PtV5rmLY"

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES['default'].update({
    'NAME': 'systori_continuous_integration',
    'TEST': {
        'SERIALIZE': False
    }
})

STATICFILES_DIRS += (
    ('editor', os.path.join(ROOT_DIR, 'editor/build/web')),
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
