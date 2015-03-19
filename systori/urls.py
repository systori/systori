from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include('systori.apps.project.api')),
    url(r'^api/', include('systori.apps.task.api')),
    url(r'^api/', include('systori.apps.document.api')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('systori.apps.project.urls')),
    url(r'', include('systori.apps.directory.urls')),
    url(r'', include('systori.apps.document.urls')),
    url(r'', include('systori.apps.main.urls')),
    url(r'', include('systori.apps.user.urls')),

    url(r'^project-(?P<project_pk>\d+)/', include('systori.apps.task.urls')),
    url(r'^templates/', include('systori.apps.task.urls')),

    url(r'^field/', include('systori.apps.field.urls')),
)