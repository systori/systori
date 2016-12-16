import os
import sys

DEFAULT_COUNTRY = "Deutschland"

GOOGLE_MAPS_API_KEY = "AIzaSyAEhGj7BuZtHzx8lHow-cm6lTCja1txOX4"

POSTGRES_SCHEMA_MODEL = 'company.Company'
SCHEMA_USER_RELATED_NAME = 'companies'

SHARED_MODELS = [
    'company.access',
    'company.worker',
    'user.user',
]

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
    'ordered_model',
    'bootstrapform',
    'datetimewidget',
    'postgres_schema',
    'systori.lib',
    'systori.apps.user',
    'systori.apps.project',
    'systori.apps.directory',
    'systori.apps.task',
    'systori.apps.document',
    'systori.apps.field',
    'systori.apps.equipment',
    'systori.apps.accounting',
    'systori.apps.main',
    'systori.apps.company',
    'systori.apps.timetracking',
)

MIDDLEWARE_CLASSES = (
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
    os.path.join(ROOT_DIR, 'locale'),
)

LATEX_WORKING_DIR = os.path.join(BASE_DIR, 'templates/document/latex')

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

# having this on by default caused a lot of problems when outputing primary keys
# and other data that needed to be machine readable
USE_L10N = False
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

DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%m/%d/%y %H:%M',        # '10/25/06 14:30'
    '%m/%d/%y',              # '10/25/06',
    '%d.%m.%Y %H:%M'
]
