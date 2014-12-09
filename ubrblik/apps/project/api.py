from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.conf.urls import url
from tastypie import fields
from tastypie import http
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils import trailing_slash
from .models import Project


class BaseMeta:
    authentication = SessionAuthentication()
    authorization = Authorization()


class ProjectResource(ModelResource):
    class Meta(BaseMeta):
        queryset = Project.objects.all()
        resource_name = 'project'


from tastypie.api import Api
api = Api()
api.register(ProjectResource())
urlpatterns = api.urls