from rest_framework.routers import SimpleRouter
from .api import DailyPlanViewSet, ProjectViewSet


router = SimpleRouter()
router.register(r"dailyplans", DailyPlanViewSet)
router.register(r"projects", ProjectViewSet)

urlpatterns = router.urls
