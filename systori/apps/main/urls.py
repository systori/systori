from django.conf.urls import url, include
from ..user.authorization import office_auth
from .views import IndexView, DayBasedOverviewView, DailyPlansPerDayJson, DailyPlanView, DailyPlanViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'dailyplans', DailyPlanViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^day-based-overview/(?P<selected_day>\d{4}-\d{2}-\d{2})?$', office_auth(DayBasedOverviewView.as_view()),
        name='day_based_overview'),
    url(r'^dailyplans-json/(?P<selected_day>\d{4}-\d{2}-\d{2})?$', office_auth(DailyPlansPerDayJson.as_view()),
        name='dailyplan_ids_per_day_view.json'),
    url(r'^dailyplan-(?P<pk>\d+)$', office_auth(DailyPlanView.as_view()),
        name='dailyplan_view'),
]
