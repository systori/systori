from systori.settings.common import *
import os

LANGUAGE_CODE = "en"
SERVER_NAME = "systori.localhost"
SESSION_COOKIE_DOMAIN = "." + SERVER_NAME
ALLOWED_HOSTS = ["." + SERVER_NAME]
INTERNAL_IPS = ("10.0.1.59", "127.0.0.1")

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEBUG = True
ENABLE_DEBUGTOOLBAR = True
DISABLE_PUSHER = True

if ENABLE_DEBUGTOOLBAR:
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

STATICFILES_DIRS += (("dart/src", "systori/dart/web"),)

DATABASES["default"].update(
    {
        "NAME": "systori_local",
        "HOST": "db",
        "USER": "postgres",
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "TEST": {"SERIALIZE": False},
    }
)

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "media"))
