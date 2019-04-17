from rest_framework.viewsets import ModelViewSet

from systori.apps.user.permissions import HasLaborerAccess
from systori.apps.company.models import Company
from systori.apps.company.serializers import CompanySerializer, UserPkSerializer


class CompanyModelViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (HasLaborerAccess,)

    action_serializers = {"for_user": UserPkSerializer}

    def get_queryset(self):
        return Company.objects.filter(workers=self.request.worker)
