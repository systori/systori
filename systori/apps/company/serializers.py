from rest_framework import serializers
from .models import Worker, Company


class UserPkSerializer(serializers.Serializer):
    user_pk = serializers.IntegerField()


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("schema", "name")


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ("first_name", "last_name")


class WorkerListingField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.user.get_full_name()}"
