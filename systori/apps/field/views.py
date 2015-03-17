from datetime import timedelta
from django.http import HttpResponseRedirect
from datetime import date
from django.db.models import Q
from django.views.generic import View, DetailView, ListView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse
from ..user.models import User
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

        context['todays_plans'] = self.request.user.todays_plans.all()

        context['previous_plans'] = self.request.user.daily_plans\
            .filter(day__gt=days_ago(5))\
            .exclude(day=date.today()).all()

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


def get_daily_plan(jobsite):
    daily_plan = jobsite.daily_plans.today().first()
    if not daily_plan:
        daily_plan = DailyPlan()
        daily_plan.jobsite = jobsite
        daily_plan.save()
    return daily_plan


class FieldAddSelfToJobSite(SingleObjectMixin, View):

    model = JobSite

    def get(self, request, *args, **kwargs):
        jobsite = self.get_object()
        daily_plan = get_daily_plan(jobsite)

        if not TeamMember.objects.filter(plan=daily_plan, member=self.request.user).exists():
            TeamMember.objects.create(
                plan = daily_plan,
                member = self.request.user,
                is_foreman = True if kwargs['role'] == 'foreman' else False
            )

        return HttpResponseRedirect(reverse('field.dashboard'))


class FieldAssignLabor(DetailView):

    model = JobSite
    template_name = "field/assign_labor.html"

    def get_context_data(self, **kwargs):
        context = super(FieldAssignLabor, self).get_context_data(**kwargs)
        context['workers'] = User.objects.filter(Q(is_laborer=True) | Q(is_foreman=True))

        context['assigned'] = []
        daily_plan = self.get_object().daily_plans.today().first()
        if daily_plan: context['assigned'] = daily_plan.team.all()

        return context

    def post(self, request, *args, **kwargs):
        jobsite = self.get_object()
        daily_plan = get_daily_plan(jobsite)

        previous_assignment = daily_plan.team.values_list('id', flat=True)

        # Add new assignments
        new_assignment = [int(id) for id in request.POST.getlist('workers')]
        for worker in new_assignment:
            if worker not in previous_assignment:
                TeamMember.objects.create(
                    plan = daily_plan,
                    member_id = worker
                )

        # Remove unchecked assignments
        for worker in previous_assignment:
            if worker not in new_assignment:
                TeamMember.objects.filter(
                    plan = daily_plan,
                    member_id = worker
                ).delete()

        #return HttpResponseRedirect(reverse('field.assign.labor', args=[request.project.id, jobsite.id]))
        return HttpResponseRedirect(reverse('field.project', args=[request.project.id]))


class FieldRemoveLabor(SingleObjectMixin, View):

    model = TeamMember

    def get(self, request, *args, **kwargs):
        self.get_object().delete()
        return HttpResponseRedirect(reverse('field.project', args=[request.project.id]))


class FieldToggleRole(SingleObjectMixin, View):

    model = TeamMember

    def get(self, request, *args, **kwargs):
        member = self.get_object()
        member.is_foreman = not member.is_foreman
        member.save()
        return HttpResponseRedirect(reverse('field.project', args=[request.project.id]))


class FieldAssignTasks(SingleObjectMixin, TemplateView):

    model = JobSite
    template_name = "field/assign_tasks.html"

    def get_context_data(self, **kwargs):
        context = super(FieldAssignTasks, self).get_context_data(**kwargs)
        return context

    def put(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('field.dashboard'))