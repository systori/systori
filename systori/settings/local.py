from .common import *

SERVER_NAME = 'systori.localhost'
SESSION_COOKIE_DOMAIN = '.'+SERVER_NAME

DEBUG = True

if False:
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'HIDE_IN_STACKTRACES': (
            'socketserver',
            'threading',
            'wsgiref',
            'debug_toolbar',
            #'django.contrib.staticfiles',
            #'django.core.servers',
            #'django.core.handlers',
            #'django.db.models.query',
            #'django.db.models.sql'
        )
    }

STATICFILES_DIRS += (
    ('dart/src', 'systori/dart/web'),
)

DATABASES['default'].update({
    'NAME': 'systori_local',
    'TEST': {
        'SERIALIZE': False
    }
})

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, 'media'))


if 'test' in sys.argv[1:]:

    class DisableMigrations:

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return "notmigrations"


    MIGRATION_MODULES = DisableMigrations()
