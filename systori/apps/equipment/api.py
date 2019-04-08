from rest_framework.generics import ListAPIView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..user.permissions import HasStaffAccess, HasLaborerAccess
from .models import Equipment, RefuelingStop, Maintenance
from .serializers import EquipmentSerializer, RefuelingStopSerializer


# ToDo: remove this list api, check clients
class EquipmentListApi(ListAPIView):
    permission_classes = (HasLaborerAccess,)
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.prefetch_related('equipment_type').all()
    serializer_class = EquipmentSerializer
    permission_classes = (HasLaborerAccess,)

    @action(detail=True)
    def refuelingstops(self, request, pk=None):
        equipment = self.get_object()
        refuelingstops = RefuelingStop.objects.filter(equipment=equipment)
        serializer = RefuelingStopSerializer(refuelingstops, many=True)
        # serializer = EquipmentSerializer(equipment)
        return Response(serializer.data)


class RefuelingStopViewSet(viewsets.ModelViewSet):
    queryset = RefuelingStop.objects.all()
    serializer_class = RefuelingStopSerializer
    permission_classes = (HasLaborerAccess, )