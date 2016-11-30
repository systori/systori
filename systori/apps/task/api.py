from django.conf.urls import url
from rest_framework import viewsets, mixins
from .models import Job
from .serializers import JobSerializer
from ..user.permissions import HasStaffAccess


class EditorAPI(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [HasStaffAccess]

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, partial=True, **kwargs)

urlpatterns = [
    url(r'^job/(?P<pk>\d+)/editor/save$', EditorAPI.as_view({'post': 'update'}), name='api.editor.save'),
]
