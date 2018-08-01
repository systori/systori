from rest_framework.serializers import ModelSerializer
from .models import Project, DailyPlan


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ("pk", "name")


class DailyPlanSerializer(ModelSerializer):
    class Meta:
        model = DailyPlan
        fields = ("pk",)
