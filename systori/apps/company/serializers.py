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
