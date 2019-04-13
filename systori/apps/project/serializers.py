from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    CharField,
    DateField,
    RelatedField,
)
from ..company.serializers import WorkerSerializer
from ..equipment.serializers import EquipmentSerializer
from .models import Project, DailyPlan, JobSite


class ProjectSearchSerializer(Serializer):
    query = CharField()


class WeekOfDailyPlansByDaySerializer(Serializer):
    selected_day = DateField()


class JobSiteField(RelatedField):
    def to_representation(self, value):
        return (value.name, value.project.name)


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ("pk", "name")


class JobSiteSerializer(ModelSerializer):
    project = ProjectSerializer(many=False, read_only=True)

    class Meta:
        model = JobSite
        fields = (
            "name",
            "project",
            "address",
            "city",
            "postal_code",
            "country",
            "latitude",
            "longitude",
        )


class DailyPlanSerializer(ModelSerializer):
    workers = WorkerSerializer(many=True, read_only=True)
    jobsite = JobSiteSerializer(many=False, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    day = DateField()

    class Meta:
        model = DailyPlan
        fields = ("pk", "day", "jobsite", "workers", "equipment", "notes")
