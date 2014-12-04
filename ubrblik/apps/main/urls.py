from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import IndexView, SettingsView

urlpatterns = patterns('',
  url(r'^$', IndexView.as_view(), name='home'),
  url(r'^settings$', login_required(IndexView.as_view()), name='settings')
)
