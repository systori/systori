from rest_framework.routers import DefaultRouter
from systori.apps.main.api import NoteModelViewSet

router = DefaultRouter()
router.register(r"note", NoteModelViewSet)

urlpatterns = router.urls
