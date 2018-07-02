from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView, SingleObjectMixin, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from ..company.models import Company
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
        kwargs["instance"] = Job(order=None, project=self.request.project)
        return kwargs


class JobCopy(SingleObjectMixin, View):
    model = Job
    SESSION_KEY = "job_copy"

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        request.session[self.SESSION_KEY] = object.pk
        return HttpResponseRedirect(object.project.get_absolute_url())


class JobPaste(JobCreate):
    SESSION_KEY = "job_pasted"

    def get_form_class(self):
        return JobPasteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.request.session[self.SESSION_KEY] = True
        kwargs["other_job"] = get_object_or_404(
            Job, pk=self.request.session[JobCopy.SESSION_KEY]
        )
        return kwargs


class JobCancelPaste(SingleObjectMixin, View):
    model = Job

    def get(self, request, *args, **kwargs):
        job = get_object_or_404(Job, pk=self.request.session[JobCopy.SESSION_KEY])
        del request.session[JobCopy.SESSION_KEY]
        return HttpResponseRedirect(job.project.get_absolute_url())


class JobImport(FormView):
    form_class = JobImportForm
    template_name = "task/job_import_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.request.project
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.request.project.get_absolute_url())
        return self.form_invalid(form)


class JobEditor(DetailView):
    model = Job
    template_name = "task/editor/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blank_group"] = Group()
        context["blank_task"] = Task()
        context["blank_lineitem"] = LineItem()
        return context

    def get_queryset(self):
        return super().get_queryset().with_hierarchy(self.request.project)


class JobProgress(UpdateView):
    model = Job
    template_name = "task/progress/main.html"
    form_class = JobProgressForm

    def get_initial(self):
        return {"progress_worker": self.request.worker.id}

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs, workers=Company.active().active_workers()
        )

    def get_success_url(self):
        return self.object.project.get_absolute_url()


class JobDelete(DeleteView):
    model = Job

    def get_success_url(self):
        return self.object.project.get_absolute_url()


class JobLock(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        job = get_object_or_404(Job, pk=kwargs["pk"])
        job.toggle_lock()
        job.save()
        return job.project.get_absolute_url()
