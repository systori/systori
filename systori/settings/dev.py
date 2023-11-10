import os
from systori.settings.common import *

SERVER_NAME = "e.dev.fynal.app"
SESSION_COOKIE_DOMAIN = "." + SERVER_NAME
ALLOWED_HOSTS = ["." + SERVER_NAME, "37.27.15.206", "127.0.0.1", "*.localhost"]
INTERNAL_IPS = ("37.27.15.206", "127.0.0.1")

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEBUG = True
ENABLE_DEBUGTOOLBAR = True
TESTING_MODE = "test" in sys.argv
DEV_MODE = DEBUG and not TESTING_MODE

if ENABLE_DEBUGTOOLBAR and DEV_MODE:
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
    DEBUG_TOOLBAR_PANELS = (
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    )

    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: DEBUG}

DATABASES["default"].update(
    {
        "NAME": "systori_local",
        "HOST": "localhost",
        "USER": "postgres",
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "dfguio22"),
        "TEST": {"SERIALIZE": False},
    }
)

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "media"))

SCHEMA_OUTPUT_FILEPATH = "/app/schema.yaml"
