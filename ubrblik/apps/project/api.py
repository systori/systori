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
from .models import Project


class BaseMeta:
    authentication = MultiAuthentication(BasicAuthentication(), SessionAuthentication())
    authorization = Authorization()

class BaseCorsResource(ModelResource):
    """
    Class implementing CORS
    """
    def create_response(self, *args, **kwargs):
        response = super(BaseCorsResource, self).create_response(*args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    def method_check(self, request, allowed=None):
        if allowed is None:
            allowed = []

        request_method = request.method.lower()
        allows = ','.join(map(str.upper, allowed))

        if request_method == 'options':
            response = HttpResponse(allows)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        if not request_method in allowed:
            response = http.HttpMethodNotAllowed(allows)
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        return request_method

class ProjectResource(BaseCorsResource):
    class Meta(BaseMeta):
        queryset = Project.objects.all()
        resource_name = 'project'


from tastypie.api import Api
api = Api()
api.register(ProjectResource())
urlpatterns = api.urls