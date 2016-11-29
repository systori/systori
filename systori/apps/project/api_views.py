from datetime import date
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from rest_framework import views
from rest_framework.response import Response
from .models import Project, DailyPlan
from ..document.models import DocumentTemplate
from ..user.permissions import HasStaffAccess


class BaseMeta:
    authentication = SessionAuthentication()
    authorization = Authorization()


class ProjectResource(ModelResource):
    class Meta(BaseMeta):
        queryset = Project.objects.without_template().all()
        resource_name = 'project'
        excludes = ['is_template']


class DailyPlanTodayResource(ModelResource):
    class Meta(BaseMeta):
        queryset = DailyPlan.objects.filter(day=date.today()).all()
        resource_name = 'daily_plan_today'


from tastypie.api import Api

api = Api()
api.register(ProjectResource())
api.register(DailyPlanTodayResource())
urlpatterns = api.urls


class DocumentTemplateView(views.APIView):
    permissions = (HasStaffAccess,)

    def get(self, request, project_pk=None, template_pk=None, **kwargs):
        project = Project.objects.get(id=project_pk)
        template = DocumentTemplate.objects.get(id=template_pk)
        rendered = template.render(project)
        return Response(rendered)