from rest_framework.viewsets import ModelViewSet
from systori.apps.user.models import User
from systori.apps.user.permissions import HasStaffAccess
from systori.apps.user.serializers import UserSerializer


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (HasStaffAccess,)
