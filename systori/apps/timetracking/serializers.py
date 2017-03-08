from rest_framework import serializers

from systori.lib.templatetags.customformatting import tosexagesimalhours
from .models import Timer
from . import utils


class TimerStartSerializer(serializers.ModelSerializer):
    starting_latitude = serializers.DecimalField(max_digits=11, decimal_places=8, required=True)
    starting_longitude = serializers.DecimalField(max_digits=11, decimal_places=8, required=True)

    class Meta:
        model = Timer
        fields = ('starting_latitude', 'starting_longitude')

    def create(self, validated_data):
        return Timer.start(worker=self.context['worker'], **validated_data)


class TimerStopSerializer(serializers.ModelSerializer):
    ending_latitude = serializers.DecimalField(max_digits=11, decimal_places=8, required=True)
    ending_longitude = serializers.DecimalField(max_digits=11, decimal_places=8, required=True)

    class Meta:
        model = Timer
        fields = ('ending_latitude', 'ending_longitude')


class TimerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Timer
        fields = ('kind', 'started', 'stopped', 'duration')

    kind = serializers.CharField(source='get_kind_display')
    started = serializers.SerializerMethodField()
    stopped = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    def get_started(self, obj):
        return utils.to_current_timezone(obj.started).strftime('%H:%M')

    def get_stopped(self, obj):
        return utils.to_current_timezone(obj.stopped).strftime('%H:%M') if obj.end else '—'

    def get_duration(self, obj):
        return tosexagesimalhours(obj.duration) if obj.duration else '—'
