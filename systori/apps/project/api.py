from django.conf.urls import url
from django.utils.translation import ugettext as _

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_206_PARTIAL_CONTENT

from ..user.permissions import HasStaffAccess, HasLaborerAccess
from .models import Project, DailyPlan
from .serializers import ProjectSerializer, DailyPlanSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (HasStaffAccess,)

    def get_queryset(self):
        return self.queryset.without_template()

    @action(methods=["get"], detail=True)
    def exists(self, request, pk=None):
        try:
            return Response(ProjectSerializer(self.get_object()).data)
        except:
            return Response(
                {"name": _("Project not found.")}, status=HTTP_206_PARTIAL_CONTENT
            )  # name is expected by the JS Client


class DailyPlanViewSet(ModelViewSet):
    queryset = DailyPlan.objects.all()
    serializer_class = DailyPlanSerializer
    permission_classes = (HasLaborerAccess,)
