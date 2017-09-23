from django.conf.urls import include, url
from ..user.authorization import field_auth
from .views import *

dailyplan_urls = [

    url(r'^paste$', field_auth(FieldPaste.as_view()), name='field.dailyplan.paste'),

    # assign-labor
    url(r'^labor$', field_auth(FieldAssignLabor.as_view()), name='field.dailyplan.assign-labor'),

    # assign-tasks
    url(r'^jobs$', field_auth(FieldGroupView.as_view()), name='field.dailyplan.group'),
    url(r'^group-(?P<group_pk>\d+)$', field_auth(FieldGroupView.as_view()), name='field.dailyplan.group'),
    url(r'^task-(?P<task_pk>\d+)$', field_auth(FieldTaskView.as_view()), name='field.dailyplan.task'),
    url(r'^task-(?P<task_pk>\d+)/upload$', field_auth(FieldTaskUploadAttachment.as_view()), name='field.dailyplan.task.upload'),
    url(r'^task-(?P<task_pk>\d+)/add$', field_auth(FieldAddTask.as_view()), name='field.dailyplan.task.add'),
    url(r'^task-(?P<task_pk>\d+)/remove$', field_auth(FieldRemoveTask.as_view()), name='field.dailyplan.task.remove'),

    # assign-equipment
    url(r'^equipment$', field_auth(FieldAssignEquipment.as_view()), name='field.dailyplan.assign-equipment'),

    # misc
    url(r'^member-(?P<pk>\d+)/toggle-role$', field_auth(FieldToggleRole.as_view()), name='field.dailyplan.toggle-role'),
    url(r'^member-(?P<pk>\d+)/remove$', field_auth(FieldMemberRemove.as_view()), name='field.dailyplan.member-remove'),
    url(r'^add-self-as-(?P<role>(foreman|laborer))$', field_auth(FieldAddSelfToDailyPlan.as_view()), name='field.dailyplan.self.add'),
    url(r'^remove-self$', field_auth(FieldRemoveSelfFromDailyPlan.as_view()), name='field.dailyplan.self.remove'),

]

project_urls = [
    url(r'^(?P<selected_day>\d{4}-\d{2}-\d{2})?$', field_auth(FieldProjectView.as_view()), name='field.project'),
    url(r'^(?P<selected_day>\d{4}-\d{2}-\d{2})/pick-jobsite$', field_auth(FieldPickJobSite.as_view()), name='field.dailyplan.pick-jobsite'),
    url(r'^(?P<selected_day>\d{4}-\d{2}-\d{2})/calendar$', field_auth(FieldProjectCalendar.as_view()), name='field.project.calendar'),
    url(r'^(?P<selected_day>\d{4}-\d{2}-\d{2})/copy/(?P<source_day>\d{4}-\d{2}-\d{2})$', field_auth(FieldCopyPasteDailyPlans.as_view()), name='field.dailyplan.copy-paste'),
]

urlpatterns = [
    url(r'^$', field_auth(FieldDashboard.as_view()), name='field.dashboard'),
    # equipment
    url(r'^equipment$', field_auth(FieldEquipmentList.as_view()), name='field.equipment'),
    url(r'^projects$', field_auth(FieldProjectList.as_view()), name='field.projects'),
    url(r'^timers$', field_auth(FieldTimersList.as_view()), name='field.timers'),
    url(r'^notes/$', field_auth(FieldNoteList.as_view()), name='field.notes.all'),
    url(r'^notes/(?P<project_pk>\d+)$', field_auth(FieldNoteList.as_view()), name='field.notes'),

    url(r'^project-(?P<project_pk>\d+)/', include(project_urls)),
    url(r'^jobsite-(?P<jobsite_pk>\d+)/(?P<dailyplan_url_id>\d{4}-\d{2}-\d{2}-\d+)/', include(dailyplan_urls)),
    url(r'^dailyplan-(?P<pk>\d+)/notes$', field_auth(FieldDailyPlanNotes.as_view()), name='field.dailyplan.save.notes'),
    url(r'^planning/(?P<selected_day>\d{4}-\d{2}-\d{2})?$', field_auth(FieldPlanning.as_view()), name='field.planning'),
    url(r'^planning/(?P<selected_day>\d{4}-\d{2}-\d{2})/generate/(?P<source_day>\d{4}-\d{2}-\d{2})$', field_auth(FieldGenerateAllDailyPlans.as_view()), name='field.planning.generate'),
    url(r'^planning/(?P<selected_day>\d{4}-\d{2}-\d{2})/toggle/(?P<toggle>(tasks|notes))$', field_auth(FieldPlanningToggle.as_view()), name='field.planning.toggle'),
    url(r'^planning/(?P<selected_day>\d{4}-\d{2}-\d{2})/delete$', field_auth(FieldDeleteDay.as_view()), name='field.planning.delete-day'),
]
