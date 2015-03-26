from django.conf.urls import patterns, include, url
from ..user.authorization import field_auth
from .views import *


dailyplan_urls = patterns('',

    # assign-labor
    url(r'^labor$', field_auth(FieldAssignLabor.as_view()), name='field.dailyplan.assign-labor'),

    # assign-tasks
    url(r'^jobs$', field_auth(FieldJobList.as_view()), name='field.dailyplan.assign-tasks'),
    url(r'^job-(?P<job_pk>\d+)$', field_auth(FieldJobView.as_view()), name='field.dailyplan.job'),
    url(r'^task-(?P<task_pk>\d+)$', field_auth(FieldTaskView.as_view()), name='field.dailyplan.task'),
    url(r'^task-(?P<task_pk>\d+)/add$', field_auth(FieldAddTask.as_view()), name='field.dailyplan.task.add'),
    url(r'^task-(?P<task_pk>\d+)/remove$', field_auth(FieldRemoveTask.as_view()), name='field.dailyplan.task.remove'),

    # misc
    url(r'^member-(?P<pk>\d+)/toggle-role$', field_auth(FieldToggleRole.as_view()), name='field.dailyplan.toggle-role'),
    url(r'^add-self-as-(?P<role>(foreman|laborer))$', field_auth(FieldAddSelfToDailyPlan.as_view()), name='field.dailyplan.self.add'),
    url(r'^remove-self$', field_auth(FieldRemoveSelfFromDailyPlan.as_view()), name='field.dailyplan.self.remove'),

)


project_urls = patterns('',
    url(r'^(?P<selected_day>\d{4}-\d{2}-\d{2})?$', field_auth(FieldProjectView.as_view()), name='field.project'),
    url(r'^(?P<selected_day>\d{4}-\d{2}-\d{2})/pick-jobsite$', field_auth(FieldPickJobSite.as_view()), name='field.dailyplan.pick-jobsite'),
    url(r'^(?P<selected_day>\d{4}-\d{2}-\d{2})/calendar$', field_auth(FieldProjectCalendar.as_view()), name='field.project.calendar'),
    url(r'^(?P<selected_day>\d{4}-\d{2}-\d{2})/copy-from/(?P<other_day>\d{4}-\d{2}-\d{2})$', field_auth(FieldGenerateProjectDailyPlans.as_view()), name='field.dailyplan.generate'),
)


urlpatterns = patterns('',
    url(r'^$', field_auth(FieldDashboard.as_view()), name='field.dashboard'),
    url(r'^projects$', field_auth(FieldProjectList.as_view()), name='field.projects'),
    url(r'^project-(?P<project_pk>\d+)/', include(project_urls)),
    url(r'^jobsite-(?P<jobsite_pk>\d+)/(?P<dailyplan_url_id>\d{4}-\d{2}-\d{2}-\d+)/', include(dailyplan_urls)),
    url(r'^dailyplan-(?P<pk>\d+)/notes$', field_auth(FieldDailyPlanNotes.as_view()), name='field.dailyplan.save.notes'),
    url(r'^planning/(?P<selected_day>\d{4}-\d{2}-\d{2})?$', field_auth(FieldPlanning.as_view()), name='field.planning'),
    url(r'^planning/(?P<selected_day>\d{4}-\d{2}-\d{2})/generate$', field_auth(FieldGenerateAllDailyPlans.as_view()), name='field.planning.generate'),
    url(r'^planning/(?P<selected_day>\d{4}-\d{2}-\d{2})/toggle/(?P<toggle>(tasks|notes))$', field_auth(FieldPlanningToggle.as_view()), name='field.planning.toggle'),
)