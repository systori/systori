from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Max

from .models import *
from .forms import *


class JobCreate(CreateView):
    model = Job

    def get_form_class(self):
        if self.request.project.is_template:
            return JobTemplateCreateForm
        else:
            return JobCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        project = self.request.project
        max_code = project.jobs.all().aggregate(order=Max('order'))['order'] or 0
        kwargs['instance'] = Job(order=max_code+1, project=project)
        return kwargs


class JobEditor(DetailView):
    model = Job
    template_name = "task/editor/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blank_group'] = Group()
        context['blank_task'] = Task()
        context['blank_lineitem'] = LineItem()
        return context

    def get_queryset(self):
        return super().get_queryset().with_hierarchy(self.request.project)


class JobProgress(UpdateView):
    model = Job
    template_name = "task/job_progress.html"
    form_class = JobProgressForm

    def get_queryset(self):
        return super().get_queryset() \
            .prefetch_related('all_tasks') \
            .prefetch_related('all_lineitems')

    def get_success_url(self):
        return self.object.project.get_absolute_url()

class JobDelete(DeleteView):
    model = Job

    def get_success_url(self):
        return self.object.project.get_absolute_url()
