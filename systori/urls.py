from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from apps.user.authorization import office_auth
from django.views.static import serve
from django.conf import settings


urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),

    url(r'^api/', include('systori.apps.project.api')),
    url(r'^api/', include('systori.apps.task.api')),
    url(r'^api/', include('systori.apps.document.api')),
    url(r'^api/', include('systori.apps.directory.api')),
    url(r'^api/v1/timetracking/', include('systori.apps.timetracking.api_urls')),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'', include('systori.apps.company.urls')),
    url(r'', include('systori.apps.project.urls')),
    url(r'', include('systori.apps.directory.urls')),
    url(r'', include('systori.apps.document.urls')),
    url(r'', include('systori.apps.accounting.urls')),
    url(r'', include('systori.apps.user.urls')),
    url(r'', include('systori.apps.equipment.urls')),
    url(r'', include('systori.apps.main.urls')),
    url(r'', include('systori.apps.timetracking.urls')),

    url(r'^project-(?P<project_pk>\d+)/', include('systori.apps.task.urls')),
    url(r'^templates/', include('systori.apps.task.urls')),

    url(r'^field/', include('systori.apps.field.urls')),
]

urlpatterns += staticfiles_urlpatterns()
