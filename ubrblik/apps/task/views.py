from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy

from ..project.models import Project
from .models import TaskGroup

class TaskList(SingleObjectMixin, ListView):
    template_name = "task/taskgroup_list.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Project.objects.all())
        return super(TaskList, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaskList, self).get_context_data(**kwargs)
        context['project'] = self.object
        return context

    def get_queryset(self):
        return self.object.task_groups.all()


class TaskCreate(CreateView):
    model = TaskGroup

    def get_context_data(self, **kwargs):
        context = super(TaskCreate, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        return context

    def get_success_url(self):
        return reverse('tasks', args=(self.object.project.id,))

class TaskUpdate(UpdateView):
    model = TaskGroup

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        return context

    def get_success_url(self):
        return reverse('tasks', args=(self.object.project.id,))

class TaskDelete(DeleteView):
    model = TaskGroup

    def get_context_data(self, **kwargs):
        context = super(TaskDelete, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        return context

    def get_success_url(self):
        return reverse('tasks', args=(self.object.project.id,))