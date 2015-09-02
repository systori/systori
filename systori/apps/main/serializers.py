from systori.apps.project.models import DailyPlan
from rest_framework import serializers


class DailyPlanSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DailyPlan
        fields = ('notes')