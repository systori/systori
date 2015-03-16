# Ubrblik Settings

# Django Settings

TASTYPIE_DEFAULT_FORMATS = ['json']

AUTH_USER_MODEL = 'user.User'
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

DEFAULT_COUNTRY = "Deutschland"

GOOGLE_MAPS_API_KEY = "AIzaSyAnSP6vllTFMFwyIeb7uhEkOy1t04IPg_M"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
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
    'ubrblik.lib',
    'ubrblik.apps.user',
    'ubrblik.apps.project',
    'ubrblik.apps.directory',
    'ubrblik.apps.task',
    'ubrblik.apps.document',
    'ubrblik.apps.main'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'ubrblik.middleware.locale.ForceDefaultLanguageMiddleware',
    'ubrblik.middleware.mobile.UbrMobileDetectionMiddleware',
    'django_mobile.middleware.SetFlavourMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ubrblik.apps.project.middleware.ProjectMiddleware'
)

from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS =\
    global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'django_mobile.context_processors.flavour',
)

ROOT_URLCONF = 'ubrblik.urls'

WSGI_APPLICATION = 'ubrblik.wsgi.application'

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
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}

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
MEDIA_ROOT = ''
MEDIA_URL = ''

STATICFILES_DIRS = (
    ('js', 'ubrblik/static/js'),
    ('css', 'ubrblik/static/css'),
    ('img', 'ubrblik/static/img'),
    ('fonts', 'ubrblik/static/fonts'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)
