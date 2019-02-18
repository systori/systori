from rest_framework import serializers
from .models import Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ("name", "manufacturer", "number_of_seats", "license_plate")


class EquipmentListingField(serializers.RelatedField):
    def to_representation(self, value):
        return value.__str__()
