from ..user.authorization import office_auth
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^timetracking/$', office_auth(views.HomeView.as_view()), name='timetracking'),
    url(r'^timetracking/vacation/$', office_auth(views.VacationScheduleView.as_view()), name='timetracking.vacation.schedule'),
    url(r'^timetracking/vacation/(?P<selected_year>\d{4})/$', office_auth(views.VacationScheduleView.as_view()), name='timetracking.vacation.schedule'),
    url(r'^timetracking/workers/(?P<worker_id>\d+)$',
        office_auth(views.WorkerReportView.as_view()), name='timetracking_worker'),
    url(r'^timetracking/timer/(?P<pk>\d+)/delete$',
        office_auth(views.TimerDeleteView.as_view()), name='timer.delete'),
    url(r'^timetracking/timer/(?P<selected_day>\d{4}-\d{2}-\d{2})/worker/(?P<worker_id>\d+)/delete$',
        office_auth(views.TimerDeleteSelectedDayView.as_view()), name='timer.delete.selected_day')
]
