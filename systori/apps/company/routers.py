from rest_framework.routers import SimpleRouter

from systori.apps.company.api import CompanyModelViewSet

router = SimpleRouter()
router.register(r"company", CompanyModelViewSet)

urlpatterns = router.urls
