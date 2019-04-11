import os
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from systori.apps.user.permissions import HasStaffAccess
from systori.apps.user.models import User
from systori.apps.user.serializers import UserSerializer


class SystoriAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "id": user.pk,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "pusher_key": os.environ.get("PUSHER_KEY", ""),
                "companies": [
                    {"schema": company.schema, "name": company.name}
                    for company in user.companies.all()
                ],
            }
        )


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (HasStaffAccess,)
