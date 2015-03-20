from django.conf.urls import patterns, include, url
from ..user.authorization import field_auth
from .views import *

daily_plan = patterns('',
  url(r'^jobs$', field_auth(FieldJobList.as_view()), name='field.jobs'),
  url(r'^job-(?P<job_pk>\d+)$', field_auth(FieldJobView.as_view()), name='field.job'),
  url(r'^task-(?P<task_pk>\d+)$', field_auth(FieldTaskView.as_view()), name='field.task'),
  url(r'^task-(?P<task_pk>\d+)/add$', field_auth(FieldAssignTask.as_view()), name='field.add.task'),
  url(r'^task-(?P<task_pk>\d+)/remove$', field_auth(FieldRemoveTask.as_view()), name='field.remove.task'),

  url(r'^add-self-as-(?P<role>(foreman|laborer))$', field_auth(FieldAddSelfToDailyPlan.as_view()), name='field.add.self'),
  url(r'^remove-self$', field_auth(FieldRemoveSelfFromDailyPlan.as_view()), name='field.remove.self'),

  url(r'^labor$', field_auth(FieldAssignLabor.as_view()), name='field.labor'),
  url(r'^member-(?P<pk>\d+)/toggle-role$', field_auth(FieldToggleRole.as_view()), name='field.labor.toggle.role'),
)

urlpatterns = patterns('',
  url(r'^$', field_auth(FieldDashboard.as_view()), name='field.dashboard'),
  url(r'^projects$', field_auth(FieldProjectList.as_view()), name='field.projects'),
  url(r'^project-(?P<project_pk>\d+)/$', field_auth(FieldProjectView.as_view()), name='field.project'),
  url(r'^planning/(?P<selected_day>\d{4}-\d{2}-\d{2})?$', field_auth(FieldDailyPlans.as_view()), name='field.planning'),
  url(r'^jobsite-(?P<jobsite_pk>\d+)/(?P<dailyplan_url_id>\d{4}-\d{2}-\d{2}-\d+)/', include(daily_plan)),
)