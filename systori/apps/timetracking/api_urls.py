from ..user.authorization import office_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^timer/$', login_required(views.TimerView.as_view()), name='timer'),
    url(
        r'^report/(?:(?P<year>\d{4})/(?:(?P<month>[10]\d)/)?)?$', 
        login_required(views.ReportView.as_view()), name='report'),
]
