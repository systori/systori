from .common import *
import sys

GOOGLE_MAPS_API_KEY = "AIzaSyDvwtHHJ_FrNVkbKoHoWh2r2E5PtV5rmLY"

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES['default'].update({
    'NAME': 'systori',
    'TEST': {
        'SERIALIZE': False
    }
})


class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


TESTS_IN_PROGRESS = False
if 'test' in sys.argv[1:]:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
    TESTS_IN_PROGRESS = True
    #MIGRATION_MODULES = DisableMigrations()
