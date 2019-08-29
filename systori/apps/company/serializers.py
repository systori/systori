from rest_framework import serializers
from rest_framework.fields import Field

from .models import Worker, Company


class UserPkSerializer(serializers.Serializer):
    user_pk = serializers.IntegerField()


class TimezoneSerializerField(Field):
    "Take the timezone object and make it JSON serializable"

    def to_representation(self, value):
        return value.zone

    def to_internal_value(self, data):
        return data


class CompanySerializer(serializers.ModelSerializer):
    timezone = TimezoneSerializerField()

    class Meta:
        model = Company
        fields = ("schema", "name", "timezone", "is_jobsite_required")


class WorkerSerializer(serializers.ModelSerializer):
    # fields which are only a @property in models.py
    has_owner = serializers.BooleanField(read_only=True)
    has_staff = serializers.BooleanField(read_only=True)
    has_foreman = serializers.BooleanField(read_only=True)
    has_laborer = serializers.BooleanField(read_only=True)

    class Meta:
        model = Worker
        fields = (
            "first_name",
            "last_name",
            "email",
            "language",
            "is_verified",
            "get_full_name",
            "company",
            "user",
            "is_owner",
            "has_owner",
            "is_staff",
            "has_staff",
            "is_foreman",
            "has_foreman",
            "is_laborer",
            "has_laborer",
            "is_accountant",
            "is_active",
            "can_track_time",
            "is_fake",
        )


class WorkerListingField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.user.get_full_name()}"
