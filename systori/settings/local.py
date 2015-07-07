from .testing import *

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
    ('editor', os.path.join(ROOT_DIR, 'editor/web')),
    # ('editor', os.path.join(ROOT_DIR, 'editor/build/web')),
)

DATABASES['default'].update({
    'NAME': 'systori_local'
})
