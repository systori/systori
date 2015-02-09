from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import IndexView, SettingsView, TemplatesView

urlpatterns = patterns('',
  url(r'^$', IndexView.as_view(), name='home'),
  url(r'^settings$', login_required(IndexView.as_view()), name='settings'),
  url(r'^templates$', login_required(TemplatesView.as_view()), name='templates'),
)
