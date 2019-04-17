from rest_framework.viewsets import ModelViewSet

from systori.apps.user.permissions import HasOwnerAccess
from systori.apps.company.models import Company
from systori.apps.company.serializers import CompanySerializer


class CompanyModelViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (HasOwnerAccess,)
