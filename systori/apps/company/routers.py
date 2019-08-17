from rest_framework.routers import SimpleRouter

from systori.apps.company.api import CompanyModelViewSet, WorkerModelViewSet

router = SimpleRouter()
router.register(r"company", CompanyModelViewSet)
router.register(r"worker", WorkerModelViewSet)

urlpatterns = router.urls
