# Systori Settings

# Pre-populates all addresses and used by geocoding
# for address-> lat/long coordinates.
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

DEFAULT_COUNTRY = "Deutschland"

GOOGLE_MAPS_API_KEY = "AIzaSyAEhGj7BuZtHzx8lHow-cm6lTCja1txOX4"

SCHEMA_MODEL = 'company.Company'
SCHEMA_USER_RELATED_NAME = 'companies'

SHARED_MODELS = [
    'company.access',
    'user.user',
    'tastypie.apiaccess',
    'tastypie.apikey'
]

# Django Settings

TASTYPIE_DEFAULT_FORMATS = ['json']

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

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'tastypie',
    'django_mobile',
    'ordered_model',
    'bootstrapform',
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
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'systori.middleware.mobile.UbrMobileDetectionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'systori.apps.user.middleware.SetLanguageMiddleware',
    'django_mobile.middleware.SetFlavourMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tuath.middleware.SchemaMiddleware',
    'systori.apps.company.middleware.AccessMiddleware',
    'systori.apps.project.middleware.ProjectMiddleware',
    'systori.apps.field.middleware.FieldMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.template.context_processors.debug',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.template.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django_mobile.context_processors.flavour',
)

ROOT_URLCONF = 'systori.urls'

WSGI_APPLICATION = 'systori.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

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
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'tuath.backends.postgres',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'de'


def gettext_noop(s): return lambda s: s
LANGUAGES = (
    ('de', gettext_noop('Deutsch')),
    ('en', gettext_noop('English')),
    #    ('uk', gettext_noop('Українською')),
    #    ('ru', gettext_noop('По-русски')),
)

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
STATIC_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '../static'))
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, 'media'))
MEDIA_URL = ''

STATICFILES_DIRS = (
    ('js', 'systori/static/js'),
    ('css', 'systori/static/css'),
    ('img', 'systori/static/img'),
    ('fonts', 'systori/static/fonts'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)
