import json
from datetime import date
from django.http.response import HttpResponse
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.conf.urls import url
from tastypie import fields
from tastypie import http
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication, BasicAuthentication, MultiAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils import trailing_slash
from .models import Project, DailyPlan
from ..document.models import DocumentTemplate


class BaseMeta:
    authentication = SessionAuthentication()
    authorization = Authorization()


class DocumentTemplateRendererResourceMixin:

    def prepend_urls(self):
        urls = super(DocumentTemplateRendererResourceMixin, self).prepend_urls()
        urls.append(
            url(r"^(?P<resource_name>%s)/(?P<%s>.*?)/document-template%s$" %
                (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()),
                self.wrap_view('dispatch_document_template'), name="api_dispatch_document_template")
        )
        self._meta.document_template_allowed_methods = ['get']
        return urls

    def dispatch_document_template(self, request, **kwargs):
        return self.dispatch('document_template', request, **kwargs)

    def get_document_template(self, request, **kwargs):
        project = self.obj_get(self.build_bundle(request=request), **self.remove_api_resource_names(kwargs))

        if 'templateid' not in request.GET:
            raise ValidationError("Missing 'templateid' argument.")

        templateid = request.GET['templateid']
        if not templateid:
            raise ValidationError("'templateid' is empty.")

        template = DocumentTemplate.objects.get(id=templateid)

        rendered = template.render(project)

        return http.HttpResponse(json.dumps(rendered))


class ProjectResource(DocumentTemplateRendererResourceMixin, ModelResource):
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
