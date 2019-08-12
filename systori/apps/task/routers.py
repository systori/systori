from rest_framework.routers import SimpleRouter
from systori.apps.user.authorization import office_auth
from .api import JobModelViewSet, GroupModelViewSet, TaskModelViewSet

from django.conf.urls import url

router = SimpleRouter()
router.register(r"job", JobModelViewSet)
router.register(r"group", GroupModelViewSet)
router.register(r"task", TaskModelViewSet)


urlpatterns = router.urls
