from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from . import api_views

urlpatterns = [
    url(r'^timer/$', login_required(api_views.TimerView.as_view()), name='timer'),
    url(
        r'^report/(?:(?P<year>\d{4})/(?:(?P<month>[10]\d)/)?)?$', 
        login_required(api_views.ReportView.as_view()), name='report'),

    url(r'^users/(?P<worker_id>\d+)/timers/$', api_views.TimerAdminView.as_view(), name='timer_admin'),
]
