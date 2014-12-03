from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include('ubrblik.apps.project.api')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login', 'django.contrib.auth.views.login', name="login"),
    url(r'^logout', 'django.contrib.auth.views.logout', {'next_page':'/'}, name="logout"),

    url(r'', include('ubrblik.apps.project.urls')),
    url(r'', include('ubrblik.apps.quote.urls')),
    url(r'', include('ubrblik.apps.main.urls')),
)
