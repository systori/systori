from rest_framework import serializers
from rest_framework.fields import DateTimeField
from .models import Equipment, RefuelingStop, EquipmentType


class EquipmentListingField(serializers.RelatedField):
    def to_representation(self, value):
        return value.__str__()


class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = "__all__"


class RefuelingStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefuelingStop
        fields = "__all__"


class EquipmentSerializer(serializers.ModelSerializer):
    equipment_type = EquipmentTypeSerializer(read_only=True)
    # refuelingstop_set = RefuelingStopSerializer(read_only=True, many=True)

    class Meta:
        model = Equipment
        exclude = ("last_refueling_stop", "icon")

