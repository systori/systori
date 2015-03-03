from django.views.generic import DetailView, UpdateView, TemplateView
from django.core.urlresolvers import reverse
from ..project.views import ProjectList, ProjectView
from ..task.models import Job, Task
from .forms import CompletionForm


class FieldProjectList(ProjectList):
    template_name = "field/project_list.html"


class FieldProjectView(ProjectView):
    pk_url_kwarg = 'project_pk'
    template_name = "field/project.html"


class FieldJobView(DetailView):
    model = Job
    pk_url_kwarg = 'job_pk'
    template_name = "field/job.html"


class FieldTaskView(UpdateView):
    model = Task
    pk_url_kwarg = 'task_pk'
    template_name = "field/task.html"
    form_class = CompletionForm
    def get_success_url(self):
        return reverse('field.job', args=[self.request.project.id, self.object.taskgroup.job.id])