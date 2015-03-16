from datetime import timedelta
from django.http import HttpResponseRedirect
from datetime import date
from django.views.generic import View, DetailView, ListView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse
from ..project.views import ProjectList, ProjectView
from ..project.models import DailyPlan, JobSite, TeamMember
from ..task.models import Job, Task
from .forms import CompletionForm


def days_ago(ago):
    return date.today() - timedelta(days=ago)


class FieldDashboard(TemplateView):
    template_name = "field/dashboard.html"
    def get_context_data(self, **kwargs):
        context = super(FieldDashboard, self).get_context_data(**kwargs)

        today = date.today()

        context['todays_plans'] = self.request.user.daily_plans\
            .filter(day=today).all()

        context['previous_plans'] = self.request.user.daily_plans\
            .filter(day__gt=days_ago(5)).exclude(day=today).all()

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


class FieldAddSelfToJobSite(SingleObjectMixin, View):

    model = JobSite

    def get(self, request, *args, **kwargs):
        jobsite = self.get_object()

        daily_plan = jobsite.daily_plans.first()
        if not daily_plan or not daily_plan.is_today():
            daily_plan = DailyPlan()
            daily_plan.jobsite = jobsite
            daily_plan.save()

        if not TeamMember.objects.filter(plan=daily_plan, member=self.request.user).exists():
            TeamMember.objects.create(
                plan = daily_plan,
                member = self.request.user,
                is_foreman = True if kwargs['role'] == 'foreman' else False
            )

        return HttpResponseRedirect(reverse('home'))