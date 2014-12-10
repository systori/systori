from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from ..task.models import TaskGroup
from .models import Project

class ProjectList(ListView):
    model = Project

class ProjectCreate(CreateView):
    model = Project
    success_url = reverse_lazy('projects')

    def form_valid(self, form):
        response = super(ProjectCreate, self).form_valid(form)
        TaskGroup.objects.create(name='first task group', project=self.object)
        return response

class ProjectUpdate(UpdateView):
    model = Project
    success_url = reverse_lazy('projects')

class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('projects')