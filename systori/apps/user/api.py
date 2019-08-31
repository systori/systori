from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from systori.apps.company.serializers import CompanySerializer
from systori.apps.user.permissions import WorkerIsAuthenticated
from systori.apps.user.serializers import UserSerializer


class UserMeAPIView(APIView):
    permission_classes = (WorkerIsAuthenticated,)

    @swagger_auto_schema(responses={200: UserSerializer()})
    def get(self, request):
        return Response(UserSerializer(request.user).data)


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
                "companies": [
                    CompanySerializer(company).data for company in user.companies.all()
                ],
            }
        )
