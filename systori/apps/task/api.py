from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from drf_yasg.utils import swagger_auto_schema

from rest_framework import views, viewsets, mixins
from rest_framework import response, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from systori.lib.templatetags.customformatting import ubrdecimal
from systori.apps.task.models import Job, Group, Task, LineItem
from systori.apps.task.serializers import JobSerializer
import systori.apps.task.flutter_serializers as flutter

from ..user.permissions import HasStaffAccess


class EditorAPI(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (HasStaffAccess,)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, partial=True, **kwargs)


class SearchAPI(views.APIView):

    permission_classes = (HasStaffAccess,)

    def post(self, request, *args, **kwargs):
        model_type = request.data["model_type"]
        terms = request.data["terms"]
        if model_type == "group":
            remaining_depth = int(request.data["remaining_depth"])
            return response.Response(
                list(
                    Group.objects.groups_with_remaining_depth(remaining_depth)
                    .search(terms)
                    .distinct("name", "rank")
                    .values(
                        "id", "job__name", "match_name", "match_description", "rank"
                    )[:30]
                )
            )
        elif model_type == "task":
            qs = Task.objects.raw(
                """
                    SELECT
                    task_task.id,
                    COUNT(task_lineitem.id) AS lineItemCount,
                    ts_headline('german', task_task.description, plainto_tsquery('german'::regconfig, '{terms}')) AS match_description,
                    ts_headline('german', task_task.name, plainto_tsquery('german'::regconfig, '{terms}')) AS match_name
                    FROM task_task
                    JOIN (
                    SELECT DISTINCT ON (task_task.search) * FROM task_task
                    ) distinctifier
                    ON task_task.id = distinctifier.id
                    LEFT JOIN task_lineitem ON (task_task.id = task_lineitem.task_id)
                    WHERE task_task.search @@ (plainto_tsquery('german'::regconfig, '{terms}')) = true 
                    GROUP BY task_task.id
                    ORDER BY lineItemCount DESC
                """.format(
                    terms=terms
                )
            )[:30]
            return response.Response(
                [
                    {
                        "id": task.id,
                        "match_name": task.match_name,
                        "match_description": task.match_description,
                    }
                    for task in qs
                ]
            )


class InfoAPI(views.APIView):

    permission_classes = (HasStaffAccess,)

    def get(self, request, *args, **kwargs):
        model_type = kwargs["model_type"]
        model_pk = int(kwargs["pk"])
        if model_type == "group":
            group = Group.objects.get(pk=model_pk)
            return response.Response(
                {
                    "name": group.name,
                    "description": group.description,
                    "total": ubrdecimal(group.estimate),
                }
            )
        elif model_type == "task":
            task = Task.objects.get(pk=model_pk)
            return response.Response(
                {
                    "name": task.name,
                    "description": task.description,
                    "project_string": _("Project"),
                    "project_id": task.group.job.project.id,
                    "qty": ubrdecimal(task.qty, min_significant=0),
                    "unit": task.unit,
                    "price": ubrdecimal(task.price),
                    "total": ubrdecimal(task.total),
                    "lineitems": [
                        {
                            "name": li["name"],
                            "qty": ubrdecimal(li["qty"], min_significant=0),
                            "unit": li["unit"],
                            "price": ubrdecimal(li["price"]),
                            "total": ubrdecimal(li["total"]),
                        }
                        for li in task.lineitems.values(
                            "name", "qty", "unit", "price", "total"
                        )
                    ],
                }
            )


class CloneAPI(views.APIView):

    renderer_classes = (renderers.TemplateHTMLRenderer,)
    permission_classes = (HasStaffAccess,)

    def post(self, request, *args, **kwargs):
        source_type = request.data["source_type"]
        position = request.data["position"]
        source_class = {"group": Group, "task": Task}[source_type]
        source = source_class.objects.get(pk=int(request.data["source_pk"]))
        target = Group.objects.get(pk=int(request.data["target_pk"]))
        source.clone_to(target, position)
        source = source_class.objects.get(pk=source.pk)
        return response.Response(
            {source_type: source},
            template_name="task/editor/{}_loop.html".format(source_type),
        )


class GroupModelViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = flutter.GroupSerializer
    permission_classes = (HasStaffAccess,)

    @swagger_auto_schema(
        method="POST",
        request_body=flutter.GroupSearchSerializer,
        responses={200: flutter.GroupSerializer(many=True)},
    )
    @action(methods=["POST"], detail=False)
    def search(self, request):
        search = flutter.GroupSearchSerializer(data=request.data)
        search.is_valid()
        terms = search.data["terms"]
        remaining_depth = search.data["remaining_depth"]

        result = (
            Group.objects.groups_with_remaining_depth(
                remaining_depth
            )  # filter groups valid only for remaining depth
            .search(terms)  # search
            .distinct("name", "rank")  # remove possible duplicates
            .order_by("-rank")  # Order by rank descending
        )

        return Response(data=flutter.GroupSerializer(instance=result, many=True).data)

    @swagger_auto_schema(
        method="GET", responses={200: flutter.TaskSerializer(many=True)}
    )
    @swagger_auto_schema(
        method="POST",
        request_body=flutter.TaskSerializer,
        responses={201: flutter.TaskSerializer()},
    )
    @action(methods=["GET", "POST"], detail=True)
    def tasks(self, request, pk=None):
        group = self.get_object()
        if request.method.lower() == "get":
            return Response(
                data=flutter.TaskSerializer(group.tasks.all(), many=True).data
            )

        if request.method.lower() == "post" and pk:
            serializer = flutter.TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(group=group)

            return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(data=request.method, status=HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(methods=["GET"], responses={200: flutter.TaskSerializer()})
    @swagger_auto_schema(
        methods=["PUT", "PATCH"],
        request_body=flutter.TaskSerializer,
        responses={200: flutter.TaskSerializer()},
    )
    @swagger_auto_schema(method="DELETE", responses={204: "Task deleted successfully"})
    @action(
        methods=["GET", "PUT", "PATCH", "DELETE"],
        detail=True,
        url_path=r"task/(?P<task_id>\d+)",
    )
    def task(self, request, pk=None, task_id=None):
        if not (pk or task_id):
            return Response(status=HTTP_400_BAD_REQUEST)

        group = self.get_object()
        task = get_object_or_404(group.tasks, pk=task_id)

        if request.method.lower() == "delete":
            task.delete()
            return Response(status=HTTP_204_NO_CONTENT)

        if request.method.lower() == "get":
            return Response(data=flutter.TaskSerializer(task).data)

        # This is an update request
        # We always update tasks partially
        # is_partial = request.method.lower() == "patch"
        serializer = flutter.TaskSerializer(task, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(group=group)
        return Response(data=flutter.TaskSerializer(task).data)

    @swagger_auto_schema(
        method="GET", responses={200: flutter.GroupSerializer(many=True)}
    )
    @swagger_auto_schema(
        method="POST",
        request_body=flutter.GroupSerializer,
        responses={201: flutter.GroupSerializer()},
    )
    @action(methods=["GET", "POST"], detail=True)
    def subgroups(self, request, pk=None):
        group = self.get_object()
        if request.method.lower() == "get":
            return Response(
                data=flutter.GroupSerializer(group.groups.all(), many=True).data
            )

        if request.method.lower() == "post" and pk:
            serializer = flutter.GroupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(parent=group)

            return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(data=request.method, status=HTTP_405_METHOD_NOT_ALLOWED)


class JobModelViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = flutter.JobSerializer
    permission_classes = (HasStaffAccess,)

    @swagger_auto_schema(
        method="GET", responses={200: flutter.TaskSerializer(many=True)}
    )
    @swagger_auto_schema(
        method="POST",
        request_body=flutter.TaskSerializer,
        responses={201: flutter.TaskSerializer()},
    )
    @action(methods=["GET", "POST"], detail=True)
    def tasks(self, request, pk=None):
        return GroupModelViewSet.tasks(self, request, pk=pk)

    @swagger_auto_schema(methods=["GET"], responses={200: flutter.TaskSerializer()})
    @swagger_auto_schema(
        methods=["PUT", "PATCH"],
        request_body=flutter.TaskSerializer,
        responses={200: flutter.TaskSerializer()},
    )
    @swagger_auto_schema(method="DELETE", responses={204: "Task deleted successfully"})
    @action(
        methods=["GET", "PUT", "PATCH", "DELETE"],
        detail=True,
        url_path=r"task/(?P<task_id>\d+)",
    )
    def task(self, request, pk=None, task_id=None):
        return GroupModelViewSet.task(self, request, pk=pk, task_id=task_id)

    @swagger_auto_schema(
        method="GET", responses={200: flutter.GroupSerializer(many=True)}
    )
    @swagger_auto_schema(
        method="POST",
        request_body=flutter.GroupSerializer,
        responses={201: flutter.GroupSerializer()},
    )
    @action(methods=["GET", "POST"], detail=True)
    def groups(self, request, pk=None):
        return GroupModelViewSet.subgroups(self, request, pk=pk)


class TaskModelViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = flutter.TaskSerializer
    permission_classes = (HasStaffAccess,)

    @swagger_auto_schema(
        method="POST",
        request_body=flutter.TaskSearchSerializer,
        responses={200: flutter.TaskSerializer(many=True)},
    )
    @action(methods=["POST"], detail=False)
    def search(self, request):
        search = flutter.TaskSearchSerializer(data=request.data)
        search.is_valid()
        terms = search.data["terms"]

        result = Task.objects.raw(
            """
                    SELECT
                    task_task.id,
                    COUNT(task_lineitem.id) AS lineItemCount,
                    ts_headline('german', task_task.description, plainto_tsquery('german'::regconfig, '{terms}')) AS match_description,
                    ts_headline('german', task_task.name, plainto_tsquery('german'::regconfig, '{terms}')) AS match_name
                    FROM task_task
                    JOIN (
                    SELECT DISTINCT ON (task_task.search) * FROM task_task
                    ) distinctifier
                    ON task_task.id = distinctifier.id
                    LEFT JOIN task_lineitem ON (task_task.id = task_lineitem.task_id)
                    WHERE task_task.search @@ (plainto_tsquery('german'::regconfig, '{terms}')) = true 
                    GROUP BY task_task.id
                    ORDER BY lineItemCount DESC
                """.format(
                terms=terms
            )
        )

        return Response(data=flutter.TaskSerializer(instance=result, many=True).data)

    @swagger_auto_schema(
        method="GET", responses={200: flutter.LineItemSerializer(many=True)}
    )
    @swagger_auto_schema(
        method="POST",
        request_body=flutter.LineItemSerializer,
        responses={201: flutter.LineItemSerializer()},
    )
    @action(methods=["GET", "POST"], detail=True)
    def lineitems(self, request, pk=None):
        task = self.get_object()
        if request.method.lower() == "get":
            return Response(
                data=flutter.LineItemSerializer(task.lineitems.all(), many=True).data
            )

        if request.method.lower() == "post" and pk:
            serializer = flutter.LineItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(task=task)

            return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(data=request.method, status=HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(methods=["GET"], responses={200: flutter.LineItemSerializer()})
    @swagger_auto_schema(
        methods=["PUT", "PATCH"],
        request_body=flutter.LineItemSerializer,
        responses={200: flutter.LineItemSerializer()},
    )
    @swagger_auto_schema(
        method="DELETE", responses={204: "LineItem deleted successfully"}
    )
    @action(
        methods=["GET", "PUT", "PATCH", "DELETE"],
        detail=True,
        url_path=r"lineitem/(?P<lineitem_id>\d+)",
    )
    def lineitem(self, request, pk=None, lineitem_id=None):
        if not (pk or lineitem_id):
            return Response(status=HTTP_400_BAD_REQUEST)

        task = self.get_object()

        lineitem = get_object_or_404(task.lineitems, pk=lineitem_id)

        if request.method.lower() == "delete":
            lineitem.delete()
            return Response(status=HTTP_204_NO_CONTENT)

        if request.method.lower() == "get":
            return Response(data=flutter.LineItemSerializer(lineitem).data)

        # This is an update request
        # We always update lineitems partially
        # is_partial = request.method.lower() == "patch"
        serializer = flutter.LineItemSerializer(lineitem, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task)
        return Response(data=flutter.LineItemSerializer(lineitem).data)


urlpatterns = [
    url(
        r"^editor/save/job/(?P<pk>\d+)/$",
        EditorAPI.as_view({"post": "update"}),
        name="api.editor.save",
    ),
    url(r"^editor/search$", SearchAPI.as_view(), name="api.editor.search"),
    url(
        r"^editor/info/(?P<model_type>(group|task))/(?P<pk>\d+)$",
        InfoAPI.as_view(),
        name="api.editor.info",
    ),
    url(r"^editor/clone$", CloneAPI.as_view(), name="api.editor.clone"),
]
