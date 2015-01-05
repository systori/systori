from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import ProjectList, TemplateProjectView, ProjectView, ProjectCreate, ProjectUpdate, ProjectDelete

urlpatterns = patterns('',
  url(r'^projects$', login_required(ProjectList.as_view()), name='projects'),
  url(r'^templates$', login_required(TemplateProjectView.as_view()), name='templates'),
  url(r'^create-project$', login_required(ProjectCreate.as_view()), name='project.create'),
  url(r'^project-(?P<pk>\d+)$', login_required(ProjectView.as_view()), name='project.view'),
  url(r'^project-(?P<pk>\d+)/edit$', login_required(ProjectUpdate.as_view()), name='project.edit'),
  url(r'^project-(?P<pk>\d+)/delete$', login_required(ProjectDelete.as_view()), name='project.delete'),
)