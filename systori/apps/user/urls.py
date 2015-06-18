from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import SettingsView

urlpatterns = patterns('',
                       url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'user/login.html'},
                           name="login"),
                       url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),
                       url(r'^settings$', login_required(SettingsView.as_view()), name='settings'),
                       )
