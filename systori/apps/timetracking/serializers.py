from rest_framework import serializers

from .models import Timer


class TimerStartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Timer
        fields = ('latitude', 'longitude')

    def create(self, validated_data):
        return Timer.launch(user=self.context['user'], **validated_data)
