from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import FieldDashboard, FieldProjectList, FieldProjectView, FieldJobView, FieldTaskView

field_login_required = lambda v: login_required(v, login_url='/field/')

urlpatterns = patterns('',

  url(r'^project-(?P<project_pk>\d+)/job-(?P<job_pk>\d+)/task-(?P<task_pk>\d+)/$', field_login_required(FieldTaskView.as_view()), name='field.task'),
  url(r'^project-(?P<project_pk>\d+)/job-(?P<job_pk>\d+)/$', field_login_required(FieldJobView.as_view()), name='field.job'),
  url(r'^project-(?P<project_pk>\d+)/$', field_login_required(FieldProjectView.as_view()), name='field.project'),

  url(r'^projects$', field_login_required(FieldProjectList.as_view()), name='field.projects'),
  url(r'^dashboard$', field_login_required(FieldDashboard.as_view()), name='field.dashboard'),

  url(r'^$', 'django.contrib.auth.views.login', {'template_name': 'field/login.html', }, name="field.login"),

)