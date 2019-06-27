from rest_framework import serializers

from .models import User, AuthToken
from ..company.serializers import CompanySerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class AuthTokenSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True)

    class Meta:
        model = AuthToken
        fields = (
            "token",
            "id",
            "email",
            "first_name",
            "last_name",
            "pusher_key",
            "companies",
        )
