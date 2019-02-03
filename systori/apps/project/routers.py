from rest_framework.routers import SimpleRouter
from .api import DailyPlansApiView, ProjectApiView, WeekOfDailyPlansApiView, WeekOfPlannedWorkersApiView
from django.conf.urls import url

router = SimpleRouter()
router.register(r"dailyplans", DailyPlansApiView)
router.register(r"projects", ProjectApiView)

urlpatterns = router.urls

urlpatterns += [
    url(
        r"^weekofdailyplans/(?P<day_of_week>\d{4}-\d{2}-\d{2})/$",
        WeekOfDailyPlansApiView.as_view(),
        name="api.weekofdailyplans"
    ),
    url(
        r"^weekofplannedworkers/(?P<day_of_week>\d{4}-\d{2}-\d{2})/$",
        WeekOfPlannedWorkersApiView.as_view(),
        name="api.weekofplannedworkers"
    ),
    ]