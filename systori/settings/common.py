import os
import sys

DEFAULT_COUNTRY = "Deutschland"

GOOGLE_MAPS_API_KEY = "AIzaSyAEhGj7BuZtHzx8lHow-cm6lTCja1txOX4"

BROKER_URL = 'amqp://guest:guest@192.168.0.99:5672//'
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Django Settings

AUTH_USER_MODEL = 'user.User'
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '../'))
PROJECTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '../'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8)-+y0f@(mb=!o9ov_g!+35s4ritax6jzmc*c04jo=6*5t_74&'

DEBUG = False

TESTING = 'test' in sys.argv

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django_dartium',
    'rest_framework',
    'bootstrap',
    'postgres_schema',
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
