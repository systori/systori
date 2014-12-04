from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include('ubrblik.apps.project.api')),
    url(r'^api/', include('ubrblik.apps.task.api')),
    url(r'^api/', include('ubrblik.apps.document.api')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/', 'django.contrib.auth.views.login', name="login"),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout', {'next_page':'/'}, name="logout"),

    url(r'^projects/', include('ubrblik.apps.project.urls')),
    url(r'', include('ubrblik.apps.task.urls')),
    url(r'', include('ubrblik.apps.main.urls')),
)
