from rest_framework.routers import SimpleRouter
from systori.apps.user.authorization import office_auth
from .api import DailyPlanModelViewSet, ProjectModelViewSet, ProjectSearchApi

from django.conf.urls import url

router = SimpleRouter()
router.register(r"dailyplan", DailyPlanModelViewSet)
router.register(r"project", ProjectModelViewSet)


urlpatterns = [
    # url(
    #     r"^weekofdailyplans/(?P<day_of_week>\d{4}-\d{2}-\d{2})/$",
    #     WeekOfDailyPlansListAPIView.as_view(),
    #     name="api.weekofdailyplans",
    # ),
    # url(
    #     r"^weekofplannedworkers/(?P<day_of_week>\d{4}-\d{2}-\d{2})/$",
    #     WeekOfPlannedWorkersAPIView.as_view(),
    #     name="api.weekofplannedworkers",
    # ),
    # ToDo: Delete if project_list.dart is refactored to use new api endpoint
    url(
        r"^project-search$",
        office_auth(ProjectSearchApi.as_view()),
        name="project.search",
    )
]

urlpatterns += router.urls
