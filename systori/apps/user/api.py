import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet
from rest_framework.renderers import JSONRenderer

from systori.apps.company.serializers import CompanySerializer
from systori.apps.user.models import User
from systori.apps.user.permissions import HasStaffAccess
from systori.apps.user.serializers import (
    AuthTokenSerializer,
    UserSerializer,
    AuthCredentialSerializer,
)


class SystoriAuthToken(ObtainAuthToken):
    def get_response(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        companies = CompanySerializer(user.companies.all(), many=True)
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "id": user.pk,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "pusher_key": os.environ.get("PUSHER_KEY", ""),
                "companies": JSONRenderer().render(companies.data),
            }
        )

    @swagger_auto_schema(
        deprecated=True,
        request_body=AuthCredentialSerializer,
        responses={
            HTTP_201_CREATED: openapi.Response("AuthToken", AuthTokenSerializer)
        },
    )
    def post(self, request, *args, **kwargs):
        return self.get_response(request)

    @swagger_auto_schema(
        operation_description="Login with username and password, "
        "and get auth token for subsequent operations",
        operation_summary="Login using username and password",
        operation_id="token_login",
        manual_parameters=[
            openapi.Parameter(
                "username",
                openapi.IN_QUERY,
                description="Username",
                required=True,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "password",
                openapi.IN_QUERY,
                description="Password",
                required=True,
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={HTTP_200_OK: openapi.Response("AuthToken", AuthTokenSerializer)},
    )
    def get(self, request, *args, **kwargs):
        return self.get_response(request)


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (HasStaffAccess,)
