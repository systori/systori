from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import ProjectList, ProjectView, ProjectCreate, ProjectUpdate, ProjectDelete
from .views import TemplatesView

urlpatterns = patterns('',
  url(r'^projects$', office_auth(ProjectList.as_view()), name='projects'),
  url(r'^create-project$', office_auth(ProjectCreate.as_view()), name='project.create'),
  url(r'^project-(?P<pk>\d+)$', office_auth(ProjectView.as_view()), name='project.view'),
  url(r'^project-(?P<pk>\d+)/edit$', office_auth(ProjectUpdate.as_view()), name='project.edit'),
  url(r'^project-(?P<pk>\d+)/delete$', office_auth(ProjectDelete.as_view()), name='project.delete'),
  url(r'^templates$', office_auth(TemplatesView.as_view()), name='templates'),
)