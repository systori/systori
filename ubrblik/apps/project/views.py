from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .models import Project
from .forms import ProjectForm
from ..task.models import Job, TaskGroup
from ..directory.models import ProjectContact

class ProjectList(ListView):
    model = Project
    def get_queryset(self):
        return self.model.objects.without_template()

class ProjectView(DetailView):
    model = Project

class ProjectCreate(CreateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        response = super(ProjectCreate, self).form_valid(form)
        TaskGroup.objects.create(name='',
          job=Job.objects.create(name=_('Default'), project=self.object)
        )
        return response

    def get_success_url(self):
        return reverse('project.view', args=[self.object.id])

class ProjectUpdate(UpdateView):
    model = Project
    form_class = ProjectForm
    def get_success_url(self):
        return reverse('project.view', args=[self.object.id])

class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('projects')