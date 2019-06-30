from rest_framework.routers import DefaultRouter
from .api import (
    EquipmentModelViewSet,
    EquipmentTypeModelViewSet,
    RefuelingStopModelViewSet,
    MaintenanceModelViewSet,
)

router = DefaultRouter()
router.register(r"equipment", EquipmentModelViewSet)
router.register(r"type", EquipmentTypeModelViewSet)
router.register(r"refuelingstop", RefuelingStopModelViewSet)
router.register(r"maintenance", MaintenanceModelViewSet)

urlpatterns = router.urls
