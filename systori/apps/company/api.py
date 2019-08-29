from rest_framework.viewsets import ModelViewSet

from systori.apps.user.permissions import HasLaborerAccess, HasForemanAccess
from systori.apps.company.models import Company, Worker
from systori.apps.company.serializers import (
    CompanySerializer,
    UserPkSerializer,
    WorkerSerializer,
)


class CompanyModelViewSet(ModelViewSet):

    # This is non effective, unless explicitly used, All methods in `ModelViewSet` use `get_queryset` method instead.
    # However, `rest_framework` relies on this attribute. It only needs this to provide rest api features, this should
    # be fine since internally `get_queryset` is being used
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (HasLaborerAccess,)

    action_serializers = {"for_user": UserPkSerializer}

    def get_queryset(self):
        return Company.objects.filter(workers=self.request.worker)


class WorkerModelViewSet(ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = (HasForemanAccess,)
