from rest_framework.serializers import ModelSerializer, Serializer, DecimalField

from systori.apps.timetracking.models import Timer


class TimerSerializer(ModelSerializer):
    class Meta:
        model = Timer
        fields = "__all__"


class LatLongSerializer(Serializer):
    latitude = DecimalField(max_digits=11, decimal_places=8, required=True)
    longitude = DecimalField(max_digits=11, decimal_places=8, required=True)
