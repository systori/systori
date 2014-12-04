from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from .models import Project

class ProjectList(ListView):
    model = Project

class ProjectCreate(CreateView):
    model = Project
    success_url = reverse_lazy('projects')

class ProjectUpdate(UpdateView):
    model = Project
    success_url = reverse_lazy('projects')

class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('projects')