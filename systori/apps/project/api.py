from django.utils.translation import ugettext as _
from dateutil.parser import parse as parse_date
from collections import defaultdict
import datetime

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.status import HTTP_206_PARTIAL_CONTENT, HTTP_200_OK
from rest_framework.permissions import IsAuthenticated

from ..user.permissions import HasStaffAccess, HasLaborerAccess
from .models import Project, DailyPlan
from .serializers import ProjectSerializer, DailyPlanSerializer
from ..project.serializers import WorkerSerializer, ProjectSerializer


def get_week_by_day(day):
    weekday_of_week = day.weekday()

    to_beginning_of_week = datetime.timedelta(days=weekday_of_week)
    to_end_of_week = datetime.timedelta(days=6 - weekday_of_week)

    beginning_of_week = day - to_beginning_of_week
    end_of_week = day + to_end_of_week

    return beginning_of_week, end_of_week


class ProjectApiView(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

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


class DailyPlansApiView(ModelViewSet):
    queryset = DailyPlan.objects.all()
    serializer_class = DailyPlanSerializer
    permission_classes = (HasLaborerAccess,)
    filter_backends = (SearchFilter,)
    search_fields = ('day',)


class WeekOfDailyPlansApiView(ListAPIView):
    model = DailyPlan
    serializer_class = DailyPlanSerializer
    permission_classes = (HasLaborerAccess, )

    def get_queryset(self):
        day_of_week = parse_date(self.kwargs["day_of_week"])
        beginning_of_week, end_of_week = get_week_by_day(day_of_week)

        return DailyPlan.objects\
            .select_related("jobsite__project") \
            .prefetch_related("workers__user") \
            .prefetch_related("equipment") \
            .filter(day__range=(beginning_of_week, end_of_week))


class WeekOfPlannedWorkersApiView(APIView):
    permission_classes = (HasLaborerAccess, )

    def get(self, request, *args, **kwargs):
        day_of_week = parse_date(kwargs["day_of_week"])
        beginning_of_week, end_of_week = get_week_by_day(day_of_week)

        queryset = DailyPlan.objects\
            .select_related("jobsite__project") \
            .prefetch_related("workers__user") \
            .filter(day__range=(beginning_of_week, end_of_week))

        # first setdefault key is to get and reuse a worker
        # second setdefault to have a reusable projects list
        response = dict()
        for plan in queryset:
            for worker in plan.workers.all():
                response.setdefault(worker.pk, WorkerSerializer(worker).data)
                response[worker.pk].setdefault("projects", []).append(
                    ProjectSerializer(plan.jobsite.project).data
                )

        # return a list of values to get rid of the (temporary) worker PKs
        return Response(list(response.values()))
