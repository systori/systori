from datetime import timedelta
from django.utils import timezone
from django.views.generic import DetailView, ListView, UpdateView, TemplateView
from django.core.urlresolvers import reverse
from ..project.views import ProjectList, ProjectView
from ..task.models import Job, Task
from .forms import CompletionForm


class FieldDashboard(TemplateView):
    template_name = "field/dashboard.html"
    def get_context_data(self, **kwargs):
        context = super(FieldDashboard, self).get_context_data(**kwargs)
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        context['daily_plans'] = request.user.daily_plans.filter(day__lt=seven_days_ago).all()
        return context


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