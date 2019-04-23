from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Systori API",
        default_version="v0.1",
        description="API Endpoints for Systori",
        contact=openapi.Contact(email="support@systori.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)


urlpatterns = [
    url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    url(r"^api/accounting/", include("systori.apps.accounting.routers")),
    url(r"^api/company/", include("systori.apps.company.routers")),
    url(r"^api/directory/", include("systori.apps.directory.routers")),
    url(r"^api/document/", include("systori.apps.document.routers")),
    url(r"^api/", include("systori.apps.task.api")),
    url(r"^api/", include("systori.apps.timetracking.api")),
    url(r"^api/", include("systori.apps.project.routers")),
    url(r"^api/equipment/", include("systori.apps.equipment.routers")),
    url(r"^api/main/", include("systori.apps.main.routers")),
    url(r"^api/timetracking/", include("systori.apps.timetracking.routers")),
    url(r"^i18n/", include("django.conf.urls.i18n")),
    url(r"", include("systori.apps.company.urls")),
    url(r"", include("systori.apps.project.urls")),
    url(r"", include("systori.apps.directory.urls")),
    url(r"", include("systori.apps.document.urls")),
    url(r"", include("systori.apps.accounting.urls")),
    url(r"", include("systori.apps.user.urls")),
    url(r"", include("systori.apps.equipment.urls")),
    url(r"", include("systori.apps.main.urls")),
    url(r"", include("systori.apps.timetracking.urls")),
    url(r"^project-(?P<project_pk>\d+)/", include("systori.apps.task.urls")),
    url(r"^templates/", include("systori.apps.task.urls")),
    url(r"^field/", include("systori.apps.field.urls")),
    url(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    url(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]

urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
