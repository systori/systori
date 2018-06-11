from django.conf.urls import url
from rest_framework import views
from rest_framework import response
from ..user.permissions import HasStaffAccess
from .models import Project


class ProjectAvailableAPI(views.APIView):

    permission_classes = (HasStaffAccess,)

    def get(self, request, *args, **kwargs):
        pk = int(kwargs["pk"])
        return response.Response(Project.objects.filter(pk=pk).exists())


urlpatterns = [
    url(
        r"^project-available/(?P<pk>\d+)$",
        ProjectAvailableAPI.as_view(),
        name="api.project.available",
    )
]
