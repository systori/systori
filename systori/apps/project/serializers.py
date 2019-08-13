from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    CharField,
    DateField,
    RelatedField,
    IntegerField,
    ListField,
)
from ..company.models import Worker
from ..company.serializers import WorkerSerializer
from ..equipment.serializers import EquipmentSerializer
from .models import Project, DailyPlan, JobSite


class QuerySerializer(Serializer):
    query = CharField()


class SelectedDaySerializer(Serializer):
    selected_day = DateField()


class JobSiteField(RelatedField):
    def to_representation(self, value):
        return (value.name, value.project.name)


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "pk",
            "name",
            "description",
            "is_template",
            "structure",
            "notes",
            "phase",
            "state",
        )


class ProjectSearchResultSerializer(Serializer):
    projects = ListField(child=IntegerField(), required=False)

    def create(self, validated_data):
        """
        Not actually using this serializer, Always returns `None`
        """
        return None

    def update(self, instance, validated_data):
        """
        Not actually using this serializer, Always returns `None`
        """
        return None


class WrokerWithProjectsSerializer(WorkerSerializer):
    class ProjectWithDay(ProjectSerializer):
        day = DateField(input_formats=["iso-8601"])

        class Meta:
            model = ProjectSerializer.Meta.model
            fields = ProjectSerializer.Meta.fields + ("day",)

    projects = ProjectWithDay(many=True)

    class Meta:
        model = WorkerSerializer.Meta.model
        fields = WorkerSerializer.Meta.fields + ("projects",)

    def create(self, validated_data):
        """
        Not actually using this serializer, Always returns `None`
        """
        return None

    def update(self, instance, validated_data):
        """
        Not actually using this serializer, Always returns `None`
        """
        return None


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
