from django.conf.urls import patterns, url
from ..user.authorization import field_auth
from .views import FieldProjectList, FieldProjectView, FieldJobView, FieldTaskView

urlpatterns = patterns('',
  url(r'^project-(?P<project_pk>\d+)/job-(?P<job_pk>\d+)/task-(?P<task_pk>\d+)/$', field_auth(FieldTaskView.as_view()), name='field.task'),
  url(r'^project-(?P<project_pk>\d+)/job-(?P<job_pk>\d+)/$', field_auth(FieldJobView.as_view()), name='field.job'),
  url(r'^project-(?P<project_pk>\d+)/$', field_auth(FieldProjectView.as_view()), name='field.project'),
  url(r'^projects$', field_auth(FieldProjectList.as_view()), name='field.projects'),
)