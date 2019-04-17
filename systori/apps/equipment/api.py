from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..user.permissions import HasLaborerAccess
from .models import Equipment, RefuelingStop, Maintenance
from .serializers import (
    EquipmentSerializer,
    RefuelingStopSerializer,
    MaintenanceSerializer,
)


class EquipmentModelViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.prefetch_related("equipment_type").all()
    serializer_class = EquipmentSerializer
    permission_classes = (HasLaborerAccess,)

    @action(detail=True)
    def refuelingstops(self, request, pk=None):
        equipment = self.get_object()
        refuelingstops = RefuelingStop.objects.filter(equipment=equipment)
        serializer = RefuelingStopSerializer(refuelingstops, many=True)
        return Response(serializer.data)


class RefuelingStopModelViewSet(viewsets.ModelViewSet):
    queryset = RefuelingStop.objects.all()
    serializer_class = RefuelingStopSerializer
    permission_classes = (HasLaborerAccess,)


class MaintenanceModelViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = (HasLaborerAccess,)
