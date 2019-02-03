from rest_framework import serializers
from ..company.serializers import WorkerSerializer
from ..equipment.serializers import EquipmentSerializer
from .models import Project, DailyPlan, JobSite


class JobSiteField(serializers.RelatedField):
    def to_representation(self, value):
        return (value.name, value.project.name)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("pk", "name")


class JobSiteSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(
        many=False,
        read_only=True
    )

    class Meta:
        model = JobSite
        fields = ("name", "project", "address", "city", "postal_code", "country", "latitude", "longitude")


class DailyPlanSerializer(serializers.ModelSerializer):
    workers = WorkerSerializer(many=True, read_only=True)
    jobsite = JobSiteSerializer(many=False, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    day = serializers.DateField()

    class Meta:
        model = DailyPlan
        fields = ("pk", "day", "jobsite", "workers", "equipment")
