from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import CompanySerializer
from .models import Company


class CompanyApiView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, )

    def retrieve(self, request, *args, **kwargs):
        return Response([company.schema for company in request.user.companies.all()])
