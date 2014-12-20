from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from .models import Project
from ..task.models import Job, TaskGroup

class ProjectList(ListView):
    model = Project

class ProjectCreate(CreateView):
    model = Project
    success_url = reverse_lazy('projects')

    def form_valid(self, form):
        response = super(ProjectCreate, self).form_valid(form)
        TaskGroup.objects.create(name='first task group',
          job=Job.objects.create(name="Default", project=self.object)
        )
        return response

class ProjectView(DetailView):
    model = Project

class ProjectUpdate(UpdateView):
    model = Project
    success_url = reverse_lazy('projects')

class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('projects')