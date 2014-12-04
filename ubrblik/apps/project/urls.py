from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import ProjectList, ProjectCreate, ProjectUpdate, ProjectDelete

urlpatterns = patterns('',
  url(r'^$', login_required(ProjectList.as_view()), name='projects'),
  url(r'^create$', login_required(ProjectCreate.as_view()), name='project.create'),
  url(r'^(?P<pk>\d+)/edit$', login_required(ProjectUpdate.as_view()), name='project.edit'),
  url(r'^(?P<pk>\d+)/delete$', login_required(ProjectDelete.as_view()), name='project.delete'),
)