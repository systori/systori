from django.conf.urls import url
from django.views import View
from django.template.response import TemplateResponse
from rest_framework import views, viewsets, mixins
from rest_framework import response
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


class InjectAPI(View):

    def post(self, request, *args, **kwargs):
        model_type = request.data['model_type']
        model_class = {
            'group': Group,
            'task': Task
        }[model_type]
        source = model_class.objects.get(pk=int(request.data['source_pk']))
        target = model_class.objects.get(pk=int(request.data['target_pk']))
        target.copy(source)
        return TemplateResponse(request, 'task/editor/{}_loop.html'.format(model_type), {
            model_type: target
        })


urlpatterns = [
    url(r'^job/(?P<pk>\d+)/editor/save$', EditorAPI.as_view({'post': 'update'}), name='api.editor.save'),
    url(r'^editor/search$', SearchAPI.as_view(), name='api.editor.search'),
    url(r'^editor/inject$', InjectAPI.as_view(), name='api.editor.inject'),
]
