from django.views.generic import View
from django.db.models import Q
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from dateutil.parser import parse as parse_date
import datetime

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.status import HTTP_206_PARTIAL_CONTENT
from rest_framework.permissions import IsAuthenticated

from ..user.permissions import HasLaborerAccess
from .models import Project, DailyPlan
from .serializers import DailyPlanSerializer
from systori.apps.project.serializers import (
    WorkerSerializer,
    ProjectSerializer,
    ProjectSearchSerializer,
    WeekOfDailyPlansByDaySerializer,
)


def get_week_by_day(day):
    weekday_of_week = day.weekday()

    to_beginning_of_week = datetime.timedelta(days=weekday_of_week)
    to_end_of_week = datetime.timedelta(days=6 - weekday_of_week)

    beginning_of_week = day - to_beginning_of_week
    end_of_week = day + to_end_of_week

    return beginning_of_week, end_of_week


class ProjectModelViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = None

    action_serializers = {"search": ProjectSearchSerializer}

    def get_queryset(self):
        return self.queryset.without_template()

    def get_serializer_class(self):
        if hasattr(self, "action_serializers"):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super(ProjectModelViewSet, self).get_serializer_class()

    @action(methods=["get"], detail=True)
    def exists(self, request, pk=None):
        try:
            return Response(ProjectSerializer(self.get_object()).data)
        except:
            return Response(
                {"name": _("Project not found.")}, status=HTTP_206_PARTIAL_CONTENT
            )  # name is expected by the JS Client

    @action(methods=["put"], detail=False)
    def search(self, request):
        queryset = (
            Project.objects.without_template()
            .prefetch_related("jobsites")
            .prefetch_related("project_contacts__contact")
            .prefetch_related("jobs")
            .prefetch_related("invoices")
        )

        project_filter = Q()
        searchable_paths = {}

        # search_terms = [term for term in request.GET.get("search").split(" ")]
        search_terms = [term for term in request.data["query"].split(" ")]
        for term in search_terms:
            searchable_paths[term] = (
                Q(id__icontains=term)
                | Q(name__icontains=term)
                | Q(description__icontains=term)
                | Q(jobsites__name__icontains=term)
                | Q(jobsites__address__icontains=term)
                | Q(jobsites__city__icontains=term)
                | Q(jobs__name__icontains=term)
                | Q(jobs__description__icontains=term)
                | Q(contacts__business__icontains=term)
                | Q(contacts__first_name__icontains=term)
                | Q(contacts__last_name__icontains=term)
                | Q(contacts__address__icontains=term)
                | Q(contacts__notes__icontains=term)
                | Q(project_contacts__association__icontains=term)
                | Q(invoices__invoice_no__icontains=term)
                | Q(contacts__email__icontains=term)
            )
        for key in searchable_paths.keys():
            project_filter &= searchable_paths[key]

        queryset = queryset.without_template().filter(project_filter).distinct()
        projects = [p.id for p in queryset]

        return JsonResponse({"projects": projects})


class DailyPlanModelViewSet(ModelViewSet):
    queryset = DailyPlan.objects.all()
    serializer_class = DailyPlanSerializer
    permission_classes = (HasLaborerAccess,)
    filter_backends = (SearchFilter,)
    search_fields = ("day",)

    action_serializers = {"full_week_by_day": WeekOfDailyPlansByDaySerializer}

    def get_serializer_class(self):
        if hasattr(self, "action_serializers"):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super(DailyPlanModelViewSet, self).get_serializer_class()

    @action(methods=["put"], detail=False)
    def full_week_by_day(self, request):
        selected_day = parse_date(request.data["selected_day"])
        beginning_of_week, end_of_week = get_week_by_day(selected_day)

        return DailyPlanSerializer(
            DailyPlan.objects.select_related("jobsite__project")
            .prefetch_related("workers__user")
            .prefetch_related("equipment")
            .filter(day__range=(beginning_of_week, end_of_week)),
            many=True,
        ).data


class WeekOfDailyPlansListAPIView(ListAPIView):
    model = DailyPlan
    serializer_class = DailyPlanSerializer
    permission_classes = (HasLaborerAccess,)

    def get_queryset(self):
        day_of_week = parse_date(self.kwargs["day_of_week"])
        beginning_of_week, end_of_week = get_week_by_day(day_of_week)

        return (
            DailyPlan.objects.select_related("jobsite__project")
            .prefetch_related("workers__user")
            .prefetch_related("equipment")
            .filter(day__range=(beginning_of_week, end_of_week))
        )


class WeekOfPlannedWorkersAPIView(APIView):
    permission_classes = (HasLaborerAccess,)

    def get(self, request, *args, **kwargs):
        day_of_week = parse_date(kwargs["day_of_week"])
        beginning_of_week, end_of_week = get_week_by_day(day_of_week)

        queryset = (
            DailyPlan.objects.select_related("jobsite__project")
            .prefetch_related("workers__user")
            .filter(day__range=(beginning_of_week, end_of_week))
        )

        # first setdefault key is to get and reuse a worker
        # second setdefault to have a reusable projects list
        response = dict()
        for plan in queryset:
            for worker in plan.workers.all():
                response.setdefault(worker.pk, WorkerSerializer(worker).data)
                project = ProjectSerializer(plan.jobsite.project).data
                project["day"] = plan.day.isoformat()
                response[worker.pk].setdefault("projects", []).append(project)
        # return a list of values to get rid of the (temporary) worker PKs
        return Response(list(response.values()))


# ToDo: Delete if project_list.dart is refactored to use new api endpoint
class ProjectSearchApi(View):
    def get(self, request):
        query = (
            Project.objects.without_template()
            .prefetch_related("jobsites")
            .prefetch_related("project_contacts__contact")
            .prefetch_related("jobs")
            .prefetch_related("invoices")
        )

        project_filter = Q()
        searchable_paths = {}

        search_terms = [term for term in request.GET.get("search").split(" ")]
        for term in search_terms:
            searchable_paths[term] = (
                Q(id__icontains=term)
                | Q(name__icontains=term)
                | Q(description__icontains=term)
                | Q(jobsites__name__icontains=term)
                | Q(jobsites__address__icontains=term)
                | Q(jobsites__city__icontains=term)
                | Q(jobs__name__icontains=term)
                | Q(jobs__description__icontains=term)
                | Q(contacts__business__icontains=term)
                | Q(contacts__first_name__icontains=term)
                | Q(contacts__last_name__icontains=term)
                | Q(contacts__address__icontains=term)
                | Q(contacts__notes__icontains=term)
                | Q(project_contacts__association__icontains=term)
                | Q(invoices__invoice_no__icontains=term)
                | Q(contacts__email__icontains=term)
            )
        for key in searchable_paths.keys():
            project_filter &= searchable_paths[key]

        query = query.without_template().filter(project_filter).distinct()
        projects = [p.id for p in query]

        return JsonResponse({"projects": projects})
