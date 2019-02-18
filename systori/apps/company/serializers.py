from rest_framework import serializers
from .models import Worker, Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("schema",)


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ("first_name", "last_name")


class WorkerListingField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.user.get_full_name()}"
