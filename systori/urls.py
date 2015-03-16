from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include('ubrblik.apps.project.api')),
    url(r'^api/', include('ubrblik.apps.task.api')),
    url(r'^api/', include('ubrblik.apps.document.api')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('ubrblik.apps.project.urls')),
    url(r'', include('ubrblik.apps.directory.urls')),
    url(r'', include('ubrblik.apps.document.urls')),
    url(r'', include('ubrblik.apps.main.urls')),
    url(r'', include('ubrblik.apps.user.urls')),

    url(r'^project-(?P<project_pk>\d+)/', include('ubrblik.apps.task.urls')),
    url(r'^templates/', include('ubrblik.apps.task.urls')),

    url(r'^field/', include('ubrblik.apps.field.urls')),
)