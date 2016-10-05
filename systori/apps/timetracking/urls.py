from ..user.authorization import office_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^timetracking/$', office_auth(views.HomeView.as_view()), name='timetracking'),
    url(r'^timetracking/workers/(?P<worker_id>\d+)$',
        office_auth(views.WorkerReportView.as_view()), name='timetracking_worker'),
    url(r'^timesheet/pdf/(?P<year>\d+)/(?P<month>\d+)/(?P<user_id>\d+)?$',
        office_auth(views.TimeSheetPDFView.as_view()), name='timesheet'),
]
