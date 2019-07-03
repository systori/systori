from rest_framework import serializers

from .models import User
from ..company.serializers import CompanySerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, allow_blank=False, max_length=40)
    id = serializers.IntegerField(label="User")
    email = serializers.EmailField(
        label="Email address", required=False, allow_blank=False, min_length=5
    )
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    pusher_key = serializers.CharField(
        label="Pusher Api key",
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=256,
    )
    companies = CompanySerializer(many=True)

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


class AuthCredentialSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True, allow_blank=False, min_length=1, max_length=200
    )
    password = serializers.CharField(
        required=True, allow_blank=False, min_length=1, max_length=200
    )

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
