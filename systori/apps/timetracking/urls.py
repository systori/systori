from ..user.authorization import office_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^timetracking/$', office_auth(views.HomeView.as_view()), name='timetracking'),
]
