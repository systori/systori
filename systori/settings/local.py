from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS += (
    'debug_toolbar',
)

if False:  # Enable Profile Panel
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
        'debug_toolbar.panels.sql.SQLPanel',
    )

STATICFILES_DIRS += (
    #('dart', os.path.join(ROOT_DIR, 'systori/dart/web')),
     ('dart', os.path.join(ROOT_DIR, 'systori/dart/build/web')),
)

DATABASES['default'].update({
    'NAME': 'systori_local',
    'TEST': {
        'SERIALIZE': False
    }
})
