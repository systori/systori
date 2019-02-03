from rest_framework import serializers
from ..user.serializers import UserSerializer
from .models import Worker, Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("schema", )


class WorkerSerializer(serializers.ModelSerializer):
    # worker = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Worker
        fields = ("first_name", "last_name")


class WorkerListingField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.user.get_full_name()}"
