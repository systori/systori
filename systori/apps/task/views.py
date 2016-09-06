from django.http import HttpResponseRedirect
from django.views.generic import View, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.db.models import Max

from systori.lib.accounting.tools import compute_gross_tax
from ..accounting.constants import TAX_RATE
from ..accounting.models import create_account_for_job

from .models import *
from .forms import JobForm, JobTemplateForm


class JobTransition(SingleObjectMixin, View):
    model = Job

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        transition = None
        for t in self.object.get_available_status_transitions():
            if t.name == kwargs['transition']:
                transition = t
                break

        if transition:
            getattr(self.object, transition.name)()
            self.object.save()

        return HttpResponseRedirect(reverse('project.view', args=[self.object.project.id]))


class JobEstimateModification(SingleObjectMixin, View):
    model = Job

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        assert kwargs['action'] in ['increase', 'decrease', 'reset']
        self.object.estimate_total_modify(request.user, kwargs['action'])
        return HttpResponseRedirect(reverse('project.view', args=[self.object.project.id]))


class TaskEditor(SingleObjectMixin, ListView):
    template_name = "task/editor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.object
        context['blank_taskgroup'] = TaskGroup(job=self.object, order=0)
        context['blank_task'] = Task()
        context['blank_taskinstance'] = TaskInstance()
        context['blank_lineitem'] = LineItem()
        context['tax_rate'] = TAX_RATE
        context['tax_rate_percent'] = TAX_RATE * 100
        context['job_total_net'] = self.object.estimate_total
        context['job_total_gross'], _ = compute_gross_tax(context['job_total_net'], TAX_RATE)
        return context

    def get_object(self):
        queryset = Job.objects.prefetch_related('taskgroups__tasks__taskinstances__lineitems')
        return super().get_object(queryset)

    def get_queryset(self):
        self.object = self.get_object()
        return self.object.taskgroups.all()


class JobView(DetailView):
    model = Job


def tasks_url(self):
    if self.object.project.is_template:
        return reverse('tasks', args=[self.object.id])
    else:
        return reverse('tasks', args=[self.object.project.id, self.object.id])


class JobCreate(CreateView):
    model = Job
    fields = '__all__'

    def get_form_class(self):
        if self.request.project.is_template:
            return JobTemplateForm
        else:
            return JobForm

    def get_form_kwargs(self):
        kwargs = super(JobCreate, self).get_form_kwargs()
        project = self.request.project
        max_code = project.jobs.all().aggregate(code=Max('job_code'))['code'] or 0
        kwargs['instance'] = Job(job_code=max_code+1, project=project)
        return kwargs

    def form_valid(self, form):
        response = super(JobCreate, self).form_valid(form)
        if isinstance(form, JobForm) and form.cleaned_data['job_template']:
            tmpl = form.cleaned_data['job_template']
            tmpl.clone_to(self.object)

        self.object.account = create_account_for_job(self.object)
        self.object.save()

        return response

    def get_success_url(self):
        return tasks_url(self)


class JobUpdate(UpdateView):
    model = Job
    form_class = JobForm

    def get_success_url(self):
        return tasks_url(self)


class JobDelete(DeleteView):
    model = Job

    def get_success_url(self):
        return self.object.project.get_absolute_url()


class AllProjectsProgress(ListView):
    model = ProgressReport
    queryset = model.objects.prefetch_related('task__taskgroup__job__project').prefetch_related('worker__user')
    context_object_name = 'progressreport_list'
    paginate_by = 30
