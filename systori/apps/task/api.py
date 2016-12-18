from django.conf.urls import url
from rest_framework import views, viewsets, mixins
from rest_framework import response
from .models import Job, Group
from .serializers import JobSerializer
from .serializers import AutocompleteQuerySerializer, AutocompleteGroupSerializer
from ..user.permissions import HasStaffAccess


class EditorAPI(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [HasStaffAccess]

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, partial=True, **kwargs)


class AutocompleteAPI(views.APIView):

    def post(self, request, *args, **kwargs):
        serializer = AutocompleteQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model_type = serializer.validated_data['model_type']
        terms = serializer.validated_data['terms']
        if model_type == 'group':
            position = serializer.validated_data.get('position', 1)
            groups = Group.objects.search(terms)
            results = AutocompleteGroupSerializer(
                #Group.objects.groups_with_remaining_depth(position).search(terms),
                groups,
                many=True
            )
            return response.Response(results.data)


urlpatterns = [
    url(r'^job/(?P<pk>\d+)/editor/save$', EditorAPI.as_view({'post': 'update'}), name='api.editor.save'),
    url(r'^editor/autocomplete$', AutocompleteAPI.as_view(), name='api.editor.autocomplete'),
]
