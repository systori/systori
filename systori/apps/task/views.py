from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.db.models import Max

from ..project.models import Project
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
        #max_code = project.jobs.all().aggregate(order=Max('order'))['order'] or 0
        kwargs['instance'] = Job(order=None, project=project)
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

    def get_initial(self):
        return {
            'progress_worker': self.request.worker.id
        }

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


class JobCopy(FormView):
    model = Job
    template_name = 'task/job_form.html'
    form_class = JobCopyForm

    def get_initial(self):
        initial = super(JobCopy, self).get_initial()
        initial['project_id'] = self.kwargs['project_pk']
        return initial


    def clean_project_id(self):
        raise forms.ValidationError(_("Error happened"))

    def form_valid(self, form):
        project_id = form.cleaned_data['project_id']
        project = Project.objects.get(id=project_id)
        job = Job.objects.get(id=form.cleaned_data['job_id'])
        project.receive_job(job)
        return super(JobCopy, self).form_valid(form)

    def get_success_url(self):
        return Project.objects.get(id=self.kwargs.get("project_pk")).get_absolute_url()
