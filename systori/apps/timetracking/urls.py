from ..user.authorization import office_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^timetracking/$', office_auth(views.HomeView.as_view()), name='timetracking'),
    url(r'^timetracking/users/(?P<user_id>\d+)$',
        office_auth(views.UserReportView.as_view()), name='timetracking_user'),
    url(r'^timetracking/users/(?P<user_id>\d+)/pdf/(?P<year>\d+)/(?P<month>\d+)$',
        office_auth(views.TimeSheetPDFView.as_view()), name='timetracking_pdf'),
]
