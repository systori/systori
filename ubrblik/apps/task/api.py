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
from ..project.api import ProjectResource
from .models import TaskGroup, Task, LineItem


class BaseMeta:
    authentication = SessionAuthentication()
    authorization = Authorization()


class TaskGroupResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    class Meta(BaseMeta):
        queryset = TaskGroup.objects.all()
        resource_name = "taskgroup"
        filtering = {
            "project": "exact"
        }


class TaskResource(ModelResource):
    taskgroup = fields.ForeignKey(TaskGroupResource, 'taskgroup')
    class Meta(BaseMeta):
        queryset = Task.objects.all()
        resource_name = "task"
        filtering = {
            "group": "exact"
        }


class LineItemResource(ModelResource):
    task = fields.ForeignKey(TaskResource, 'task')
    class Meta(BaseMeta):
        queryset = LineItem.objects.all()
        resource_name = "lineitem"
        filtering = {
            "task": "exact"
        }


from tastypie.api import Api
api = Api()
api.register(TaskGroupResource())
api.register(TaskResource())
api.register(LineItemResource())
urlpatterns = api.urls