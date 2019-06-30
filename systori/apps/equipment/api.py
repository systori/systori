from django import forms
from drf_yasg import openapi
from drf_yasg.openapi import Response as OpenApiResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_417_EXPECTATION_FAILED,
)

from systori.apps.main.swagger_schema import SwaggerSchema

from ..user.permissions import HasLaborerAccess
from .models import Equipment, EquipmentType, Maintenance, RefuelingStop
from .serializers import (
    EquipmentSerializer,
    EquipmentTypeSerializer,
    MaintenanceSerializer,
    RefuelingStopSerializer,
)


# We can't use `EquipmentForm` because it has fields that are required
class ImageUploadForm(forms.Form):
    """Generic Image upload form"""

    file = forms.ImageField(required=True)


class EquipmentModelViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.prefetch_related("equipment_type").all()
    serializer_class = EquipmentSerializer
    permission_classes = (HasLaborerAccess,)
    refuelingstops_response = OpenApiResponse(
        "Refueling Stops", RefuelingStopSerializer(many=True)
    )

    @swagger_auto_schema(responses={200: refuelingstops_response})
    @action(detail=True)
    def refuelingstops(self, request, pk=None):
        equipment = self.get_object()
        refuelingstops = RefuelingStop.objects.filter(equipment=equipment)
        serializer = RefuelingStopSerializer(refuelingstops, many=True)
        return Response(serializer.data)

    icon_response = OpenApiResponse(
        "Icon",
        openapi.Schema("url", type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
    )

    icon_file = openapi.Parameter(
        "file", in_=openapi.IN_FORM, type=openapi.TYPE_FILE, required=True
    )

    @swagger_auto_schema(method="GET", responses={200: icon_response})
    @swagger_auto_schema(
        method="POST",
        manual_parameters=[icon_file],
        responses={201: icon_response},
        consumes=["application/x-www-form-urlencoded", "multipart/form-data"],
        auto_schema=SwaggerSchema,
        auto_include_parameters=False,
    )
    @action(methods=["GET", "POST"], detail=True, parser_classes=[MultiPartParser])
    def icon(self, request, pk=None):
        equipment = self.get_object()

        # Create/Update the icon
        if request.method.lower() == "post":
            form = ImageUploadForm(request.POST, request.FILES)
            form.is_valid()
            if not form.cleaned_data["file"]:
                return Response(status=HTTP_417_EXPECTATION_FAILED)
            equipment.icon = form.cleaned_data["file"]
            equipment.save()

            return Response(
                self.get_serializer(equipment).data["icon"], status=HTTP_201_CREATED
            )

        # Get the current icon
        if request.method.lower() == "get":
            if equipment.icon and equipment.icon.url:
                return Response(self.get_serializer(equipment).data["icon"])
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(data=request.method, status=HTTP_405_METHOD_NOT_ALLOWED)


class EquipmentTypeModelViewSet(viewsets.ModelViewSet):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer
    permission_classes = (HasLaborerAccess,)


class RefuelingStopModelViewSet(viewsets.ModelViewSet):
    queryset = RefuelingStop.objects.all()
    serializer_class = RefuelingStopSerializer
    permission_classes = (HasLaborerAccess,)


class MaintenanceModelViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = (HasLaborerAccess,)
