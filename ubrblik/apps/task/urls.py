from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import TaskList, TaskCreate, TaskUpdate, TaskDelete

urlpatterns = patterns('',
  url(r'^project/(?P<pk>\d+)/tasks$', login_required(TaskList.as_view()), name='tasks'),
  url(r'^project/(?P<pk>\d+)/task/create$', login_required(TaskCreate.as_view()), name='task.create'),
  url(r'^task/(?P<pk>\d+)/edit$', login_required(TaskUpdate.as_view()), name='task.edit'),
  url(r'^task/(?P<pk>\d+)/delete$', login_required(TaskDelete.as_view()), name='task.delete'),
)