from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.conf.urls import url
from django.db.models import Q
from django.template.loader import get_template
from django.template import Context
from tastypie import fields
from tastypie import http
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils import trailing_slash
from ..project.api import ProjectResource
from .models import Job, TaskGroup, Task, TaskInstance, LineItem


class BaseMeta:
    authentication = SessionAuthentication()
    authorization = Authorization()


class OrderedModelResourceMixin:

    def prepend_urls(self):
        urls = super(OrderedModelResourceMixin, self).prepend_urls()
        urls.append(
            url(r"^(?P<resource_name>%s)/(?P<%s>.*?)/move%s$" %
                (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()),
                self.wrap_view('dispatch_move'), name="api_dispatch_move")
        )
        self._meta.move_allowed_methods = ['get']
        return urls

    def dispatch_move(self, request, **kwargs):
        return self.dispatch('move', request, **kwargs)

    def get_move(self, request, **kwargs):
        obj = self.obj_get(self.build_bundle(request=request), **self.remove_api_resource_names(kwargs))

        if 'position' not in request.GET:
            raise ValidationError("Missing 'position' argument.")

        position = request.GET['position'] or '0'
        try:
            position = int(position)
        except:
            raise ValidationError("'position' must be an integer")

        obj.to(position)

        return http.HttpAccepted()

class ClonableModelResourceMixin:

    def prepend_urls(self):
        urls = super(ClonableModelResourceMixin, self).prepend_urls()
        urls.append(
            url(r"^(?P<resource_name>%s)/(?P<%s>.*?)/clone%s$" %
                (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()),
                self.wrap_view('dispatch_clone'), name="api_dispatch_clone")
        )
        self._meta.clone_allowed_methods = ['post']
        return urls

    def dispatch_clone(self, request, **kwargs):
        return self.dispatch('clone', request, **kwargs)

    def post_clone(self, request, **kwargs):
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        obj = self.obj_get(self.build_bundle(request=request), **self.remove_api_resource_names(kwargs))

        if 'target' not in data or 'pos' not in data:
            raise ValidationError("Need target and pos for clone operation.")

        template, context = self.perform_cloning(obj, data['target'], data['pos'])

        rendered = template.render(Context(context)).encode('utf-8')

        return http.HttpCreated(rendered)


class AutoCompleteModelResourceMixin:

    def prepend_urls(self):
        urls = super(AutoCompleteModelResourceMixin, self).prepend_urls()
        urls.append(
            url(r"^(?P<resource_name>%s)/autocomplete%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_autocomplete'), name="api_dispatch_autocomplete")
        )
        self._meta.autocomplete_allowed_methods = ['get']
        return urls

    def dispatch_autocomplete(self, request, **kwargs):
        return self.dispatch('autocomplete', request, **kwargs)

    def get_autocomplete(self, request, **kwargs):
        if 'query' not in request.GET:
            raise ValidationError("Missing 'query' argument.")
        
        search_string = request.GET['query']
        if not search_string:
            raise ValidationError("Search string is empty.")

        query = self._meta.queryset.\
                filter(Q(name__icontains=search_string) | Q(description__icontains=search_string))

        self.add_prefetching(query)

        template = get_template('task/{}_autocomplete.html'.format(self._meta.resource_name))
        context = Context({'objects': query.all()})
        rendered = template.render(context).encode('utf-8')

        return http.HttpResponse(rendered)


class JobResource(OrderedModelResourceMixin, ModelResource):

    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta(BaseMeta):
        queryset = Job.objects.all()
        resource_name = 'job'
        filtering = {
            "project": "exact"
        }


class TaskGroupResource(OrderedModelResourceMixin, ClonableModelResourceMixin, AutoCompleteModelResourceMixin, ModelResource):

    job = fields.ForeignKey(JobResource, 'job')

    class Meta(BaseMeta):
        queryset = TaskGroup.objects.all()
        resource_name = "taskgroup"
        filtering = {
            "job": "exact"
        }

    def perform_cloning(self, specimen, new_parent_uri, new_pos):
        job = JobResource().get_via_uri(new_parent_uri)
        specimen.clone_to(job, new_pos)
        return get_template('task/taskgroup_loop.html'), {'group': specimen}

    def add_prefetching(self, query):
        # TODO: Add prefetching.
        pass


class TaskResource(OrderedModelResourceMixin, ClonableModelResourceMixin, AutoCompleteModelResourceMixin, ModelResource):

    taskgroup = fields.ForeignKey(TaskGroupResource, 'taskgroup')

    class Meta(BaseMeta):
        queryset = Task.objects.all()
        resource_name = "task"
        filtering = {
            "taskgroup": "exact"
        }

    def perform_cloning(self, specimen, new_parent_uri, new_pos):
        taskgroup = TaskGroupResource().get_via_uri(new_parent_uri)
        specimen.clone_to(taskgroup, new_pos)
        return get_template('task/task_loop.html'), {'task': specimen}

    def add_prefetching(self, query):
        # TODO: Add prefetching.
        pass

class TaskInstanceResource(OrderedModelResourceMixin, ModelResource):
    task = fields.ForeignKey(TaskResource, 'task')
    class Meta(BaseMeta):
        queryset = TaskInstance.objects.all()
        resource_name = "taskinstance"
        filtering = {
            "task": "exact"
        }


class LineItemResource(ModelResource):
    taskinstance = fields.ForeignKey(TaskInstanceResource, 'taskinstance')
    class Meta(BaseMeta):
        queryset = LineItem.objects.all()
        resource_name = "lineitem"
        filtering = {
            "taskinstance": "exact"
        }


from tastypie.api import Api
api = Api()
api.register(JobResource())
api.register(TaskGroupResource())
api.register(TaskResource())
api.register(TaskInstanceResource())
api.register(LineItemResource())
urlpatterns = api.urls