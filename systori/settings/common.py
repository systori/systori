import os
import sys

SECRET_KEY = os.environ.get('SECRET_KEY', 'abc123')
INTERCOM_ACCESS_TOKEN = os.environ.get('INTERCOM_ACCESS_TOKEN', '')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

DEFAULT_COUNTRY = "Deutschland"

BROKER_URL = 'amqp://guest:guest@192.168.0.99:5672//'
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

# Django Settings

AUTH_USER_MODEL = 'user.User'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '../'))
PROJECTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '../'))

SITE_ID = 1

EMAIL_HOST = 'mail'
DEFAULT_FROM_EMAIL = 'Systori <support@systori.com>'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

DEBUG = False

TESTING = 'test' in sys.argv

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django_dartium',
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'bootstrap',
    'postgres_schema',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'systori.lib',
    'systori.apps.user',
    'systori.apps.main',
    'systori.apps.company',
    'systori.apps.project',
    'systori.apps.directory',
    'systori.apps.task',
    'systori.apps.document',
    'systori.apps.field',
    'systori.apps.equipment',
    'systori.apps.accounting',
    'systori.apps.timetracking',
    'systori.apps.inventory',
)

POSTGRES_SCHEMA_MODEL = 'company.Company'
POSTGRES_SCHEMA_TENANTS = (
    'company.Labor',
    'main',
    'project',
    'directory',
    'task',
    'document',
    'field',
    'equipment',
    'accounting',
    'timetracking',
    'inventory',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'systori.middleware.mobile.MobileDetectionMiddleware',
    'django_dartium.middleware.DartiumDetectionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'systori.apps.user.middleware.SetLanguageMiddleware',
    'systori.middleware.mobile.SetFlavourMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'systori.apps.company.middleware.CompanyMiddleware',
    'systori.apps.company.middleware.WorkerMiddleware',
    'systori.apps.project.middleware.ProjectMiddleware',
    'systori.apps.field.middleware.FieldMiddleware'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'systori.urls'

WSGI_APPLICATION = 'systori.wsgi.application'
ASGI_APPLICATION = 'systori.routing.application'

FIXTURE_DIRS = (
    os.path.join(ROOT_DIR, 'fixtures'),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

FORMAT_MODULE_PATH = (
    'systori.locale',
)

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'systori.db',
    }
}


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# DRF Authentication settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}


# Django Allauth Configuration
# http://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = "systori.apps.user.account.AccountAdapter"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_SIGNUP_FORM_CLASS = "systori.apps.user.forms.SignupForm"
SOCIALACCOUNT_ADAPTER = "systori.apps.user.account.SocialAccountAdapter"


GEOCODE_ADDRESSES = True

if TESTING:

    GEOCODE_ADDRESSES = False

    # in Django 2.1 this will be the default:
    TEMPLATES[0]['OPTIONS']['debug'] = True

    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    MIGRATION_MODULES = DisableMigrations()

    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'de'

gettext_noop = lambda s: s
LANGUAGES = (
    ('de', gettext_noop('Deutsch')),
    ('en', gettext_noop('English')),
    #    ('uk', gettext_noop('Українською')),
    #    ('ru', gettext_noop('По-русски')),
)

# used by postgresql full text indexing
# TODO: refactor to use be configurable per-Company schema
SEARCH_VECTOR_LANGUAGE = 'german'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True

# First and foremost, USE_L10N is dangerous business because it localizes everything.
# Including primary keys or other output that is meant to be machine readable and should
# not actually be formatted in anyway. We've gone back and forth on having this setting
# on or off. Ultimately, because Django requires this for form handling, we decided to
# enable it and then just be very careful about rendering any machine readable text by
# wrapping it in {% localize off %} and thoroughly testing.
USE_L10N = True
USE_THOUSAND_SEPARATOR = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

# this is where files are copied when running ./manage.py collectstatic
STATIC_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '..', 'static'))
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '..', 'media'))
MEDIA_URL = ''

STATICFILES_DIRS = (
    ('js', 'systori/static/js'),
    ('css', 'systori/static/css'),
    ('img', 'systori/static/img'),
    ('fonts', 'systori/static/fonts'),
    ('dart/build', 'systori/dart/build/web'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)
