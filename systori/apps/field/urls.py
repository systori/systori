from django.conf.urls import patterns, url
from ..user.authorization import field_auth
from .views import *

urlpatterns = patterns('',

  url(r'^project-(?P<project_pk>\d+)/job-(?P<job_pk>\d+)/task-(?P<task_pk>\d+)/$', field_auth(FieldTaskView.as_view()), name='field.task'),
  url(r'^project-(?P<project_pk>\d+)/job-(?P<job_pk>\d+)/$', field_auth(FieldJobView.as_view()), name='field.job'),
  url(r'^project-(?P<project_pk>\d+)/$', field_auth(FieldProjectView.as_view()), name='field.project'),

  url(r'^project-(?P<project_pk>\d+)/jobsite-(?P<pk>\d+)/add-self-as-(?P<role>(foreman|laborer))$', field_auth(FieldAddSelfToJobSite.as_view()), name='field.add_self_to_jobsite'),
  url(r'^project-(?P<project_pk>\d+)/jobsite-(?P<pk>\d+)/assign-labor$', field_auth(FieldAssignLabor.as_view()), name='field.assign.labor'),
  url(r'^project-(?P<project_pk>\d+)/member-(?P<pk>\d+)/remove$', field_auth(FieldRemoveLabor.as_view()), name='field.remove.labor'),
  url(r'^project-(?P<project_pk>\d+)/member-(?P<pk>\d+)/toggle-role$', field_auth(FieldToggleRole.as_view()), name='field.toggle.role'),
  url(r'^project-(?P<project_pk>\d+)/jobsite-(?P<pk>\d+)/assign-tasks$', field_auth(FieldAssignTasks.as_view()), name='field.assign.tasks'),

  url(r'^projects$', field_auth(FieldProjectList.as_view()), name='field.projects'),

  url(r'^$', field_auth(FieldDashboard.as_view()), name='field.dashboard'),
)