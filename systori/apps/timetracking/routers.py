from rest_framework.routers import DefaultRouter

from systori.apps.timetracking.api import TimerModelViewSet

router = DefaultRouter()
router.register(r"timer", TimerModelViewSet)

urlpatterns = router.urls
