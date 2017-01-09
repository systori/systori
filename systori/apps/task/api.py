from django.conf.urls import url
from rest_framework import views, viewsets, mixins
from rest_framework import response, renderers
from .models import Job, Group, Task
from .serializers import JobSerializer
from ..user.permissions import HasStaffAccess


class EditorAPI(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [HasStaffAccess]

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, partial=True, **kwargs)


class SearchAPI(views.APIView):

    def post(self, request, *args, **kwargs):
        model_type = request.data['model_type']
        terms = request.data['terms']
        if model_type == 'group':
            remaining_depth = int(request.data['remaining_depth'])
            return response.Response(list(
                Group.objects
                .groups_with_remaining_depth(remaining_depth)
                .search(terms)
                .values_list(
                    'id', 'match_name', 'match_description'
                )[:10]
            ))
        elif model_type == 'task':
            return response.Response(list(
                Task.objects
                    .search(terms)
                    .values_list(
                    'id', 'match_name', 'match_description'
                )[:10]
            ))


class CloneAPI(views.APIView):

    renderer_classes = (renderers.TemplateHTMLRenderer,)

    def post(self, request, *args, **kwargs):
        source_type = request.data['source_type']
        position = request.data['position']
        source_class = {
            'group': Group,
            'task': Task
        }[source_type]
        source = source_class.objects.get(pk=int(request.data['source_pk']))
        target = Group.objects.get(pk=int(request.data['target_pk']))
        source.clone_to(target, position)
        source = source_class.objects.get(pk=source.pk)
        return response.Response(
            {source_type: source}, template_name='task/editor/{}_loop.html'.format(source_type)
        )


urlpatterns = [
    url(r'^job/(?P<pk>\d+)/editor/save$', EditorAPI.as_view({'post': 'update'}), name='api.editor.save'),
    url(r'^editor/search$', SearchAPI.as_view(), name='api.editor.search'),
    url(r'^editor/clone$', CloneAPI.as_view(), name='api.editor.clone'),
]
