from rest_framework.routers import DefaultRouter

from systori.apps.directory.api import ContactModelViewSet, ProjectContactModelViewSet

router = DefaultRouter()

router.register(r"contact", ContactModelViewSet)
router.register(r"projectcontact", ProjectContactModelViewSet)

urlpatterns = router.urls
