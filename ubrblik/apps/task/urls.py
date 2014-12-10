from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import TaskList

urlpatterns = patterns('',
  url(r'^project/(?P<pk>\d+)/tasks$', login_required(TaskList.as_view()), name='tasks'),
)