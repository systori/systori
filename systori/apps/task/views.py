from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView
from django.db.models import Max

from .models import *
from .forms import JobCreateForm, JobTemplateCreateForm


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
        context['job'] = self.object
        context['blank_group'] = Group()
        context['blank_task'] = Task()
        context['blank_lineitem'] = LineItem()
        return context

    def get_queryset(self):
        return super().get_queryset().with_hierarchy(self.request.project)


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

        return HttpResponseRedirect(self.object.project.get_absolute_url())


class JobDelete(DeleteView):
    model = Job

    def get_success_url(self):
        return self.object.project.get_absolute_url()
