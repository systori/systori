from django.http import HttpResponseRedirect
from django.views.generic import View, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

from .models import Job, TaskGroup
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


class TaskEditor(SingleObjectMixin, ListView):
    template_name = "task/editor.html"

    def get_context_data(self, **kwargs):
        context = super(TaskEditor, self).get_context_data(**kwargs)
        context['job'] = self.object
        return context

    def get_object(self):
        queryset = Job.objects.all()
        return super(TaskEditor, self).get_object(queryset)

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

    def get_form_class(self):
        if self.request.project.is_template:
            return JobTemplateForm
        else:
            return JobForm

    def get_form_kwargs(self):
        kwargs = super(JobCreate, self).get_form_kwargs()
        kwargs['instance'] = Job(project=self.request.project)
        return kwargs

    def form_valid(self, form):
        response = super(JobCreate, self).form_valid(form)
        if isinstance(form, JobForm) and form.cleaned_data['job_template']:
            tmpl = form.cleaned_data['job_template']
            tmpl.clone_to(self.object)
        else:
            TaskGroup.objects.create(name='first task group', job=self.object)
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
