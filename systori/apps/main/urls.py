from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import IndexView, DayBasedOverviewView


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^day-based-overview$', office_auth(DayBasedOverviewView.as_view()), name='day_based_overview'),
)