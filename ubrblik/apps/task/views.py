import os.path, shutil
from subprocess import Popen, PIPE
from tempfile import TemporaryDirectory

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.loader import get_template
from django.template import Context

from .models import Job, TaskGroup
from .forms import JobForm

from ubrblik import settings


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


class BaseJobTaskView(SingleObjectMixin, ListView):

    def get_context_data(self, **kwargs):
        context = super(BaseJobTaskView, self).get_context_data(**kwargs)
        context['job'] = self.object
        return context

    def get_object(self):
        queryset = Job.objects.all()
        return super(BaseJobTaskView, self).get_object(queryset)

    def get_queryset(self):
        self.object = self.get_object()
        return self.object.taskgroups.all()


class TaskEditor(BaseJobTaskView):
    template_name = "task/editor.html"


TASK_TEMPLATE_DIR = 'ubrblik/templates/task/'

class TaskPDF(BaseJobTaskView):
    template_name = "task/report.tex"

    def render_to_response(self, context):
        
        template = get_template(self.template_name)
        rendered_tpl = template.render(Context(context)).encode('utf-8')

        with TemporaryDirectory() as tempdir:
            # Create subprocess, supress output with PIPE and 
            # run latex twice to generate the TOC properly. 
            # Finally read the generated pdf.

            for i in range(2):
                process = Popen(
                    ['pdflatex', '-output-directory', tempdir],
                    stdin=PIPE,
                    stdout=PIPE,
                    cwd=TASK_TEMPLATE_DIR
                )
                process.communicate(rendered_tpl)

            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()

            if settings.DEBUG:
              # make a copy of everything that was generated, including latex and
              # log file so that it can be reviewed for debugging purposes
              output_dir = os.path.join(TASK_TEMPLATE_DIR, 'output')
              shutil.rmtree(output_dir, True)
              shutil.copytree(tempdir, output_dir)
              with open(os.path.join(TASK_TEMPLATE_DIR, 'output/texput.tex'), 'wb') as tmpl:
                tmpl.write(rendered_tpl)

        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename=' + 'report.pdf'
        response.write(pdf)

        return response


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
        if isinstance(form, JobForm) and form.cleaned_data['template_job']:
            tmpl = form.cleaned_data['template_job']
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