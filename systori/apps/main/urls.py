from django.conf.urls import url
from ..user.authorization import office_auth
from .views import IndexView, DayBasedOverviewView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^day-based-overview/(?P<selected_day>\d{4}-\d{2}-\d{2})?$', office_auth(DayBasedOverviewView.as_view()),
        name='day_based_overview'),
]
