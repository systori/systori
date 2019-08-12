from rest_framework.routers import SimpleRouter
from systori.apps.user.authorization import office_auth
from .api import JobModelViewSet

from django.conf.urls import url

router = SimpleRouter()
router.register(r"job", JobModelViewSet)


urlpatterns = router.urls
