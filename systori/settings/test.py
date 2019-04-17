from systori.settings.common import *

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SERVER_NAME = "systori.localhost"
SESSION_COOKIE_DOMAIN = "." + SERVER_NAME
ALLOWED_HOSTS = ["." + SERVER_NAME]

# STATIC_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "static"))
# STATICFILES_DIRS += (("dart", "systori/dart/build/web"),)
# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "media"))

DATABASES["default"].update(
    {
        "HOST": "localhost",
        "PORT": 5432,
        "NAME": "systori_test",
        "USER": "postgres",
        "TEST": {"SERIALIZE": False},
    }
)

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

GOOGLE_MAPS_API_KEY = "AIzaSyDvwtHHJ_FrNVkbKoHoWh2r2E5PtV5rmLY"
