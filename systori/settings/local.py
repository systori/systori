from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

if True:
    INSTALLED_APPS += (
        #'debug_toolbar',
    )
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.sql.SQLPanel',
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
     ('dart', os.path.join(ROOT_DIR, 'systori/dart/web')),
    #('dart', os.path.join(ROOT_DIR, 'systori/dart/build/web')),
)

DATABASES['default'].update({
    'NAME': 'systori_local',
    'TEST': {
        'SERIALIZE': False
    }
})
