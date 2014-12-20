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
from .models import Job, TaskGroup, Task, LineItem


class BaseMeta:
    authentication = SessionAuthentication()
    authorization = Authorization()


class OrderedModelResource(ModelResource):
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<%s>.*?)/move%s$" %
                (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()),
                self.wrap_view('dispatch_move'), name="api_dispatch_move"),
            ]

    def dispatch_move(self, request, **kwargs):
        return self.dispatch('move', request, **kwargs)

    def post_move(self, request, **kwargs):
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        obj = self.obj_get(self.build_bundle(request=request), **self.remove_api_resource_names(kwargs))

        if 'target' not in data or 'pos' not in data:
            raise ValidationError("Need target and pos for move operation.")

        target = self.get_via_uri(data['target'])
        obj.move(target, data['pos'])

        return http.HttpAccepted()


class JobResource(OrderedModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    class Meta(BaseMeta):
        queryset = Job.objects.all()
        resource_name = 'job'
        filtering = {
            "project": "exact"
        }


class TaskGroupResource(ModelResource):
    job = fields.ForeignKey(JobResource, 'job')
    class Meta(BaseMeta):
        queryset = TaskGroup.objects.all()
        resource_name = "taskgroup"
        filtering = {
            "job": "exact"
        }


class TaskResource(ModelResource):
    taskgroup = fields.ForeignKey(TaskGroupResource, 'taskgroup')
    class Meta(BaseMeta):
        queryset = Task.objects.all()
        resource_name = "task"
        filtering = {
            "taskgroup": "exact"
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
api.register(JobResource())
api.register(TaskGroupResource())
api.register(TaskResource())
api.register(LineItemResource())
urlpatterns = api.urls