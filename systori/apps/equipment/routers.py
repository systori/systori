from rest_framework.routers import DefaultRouter
from .api import EquipmentModelViewSet, RefuelingStopModelViewSet

router = DefaultRouter()
router.register(r"equipment", EquipmentModelViewSet)
router.register(r"refuelingstop", RefuelingStopModelViewSet)

urlpatterns = router.urls
