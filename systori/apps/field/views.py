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


class FieldDailyPlans(TemplateView):
    template_name = "field/dailies.html"

    def get_context_data(self, **kwargs):
        context = super(FieldDailyPlans, self).get_context_data(**kwargs)

        selected_day = date.today()
        if kwargs.get('selected_day'):
            selected_day = date(*map(int, kwargs['selected_day'].split('-')))

        context['today_url'] = reverse('field.dailies', args=[date.today().isoformat()])

        context['previous_day'] = selected_day-timedelta(days=1)
        context['previous_day_url'] = reverse('field.dailies', args=[context['previous_day'].isoformat()])
        context['previous_exists'] = DailyPlan.objects.filter(day=context['previous_day']).exists()

        context['selected_day'] = selected_day
        context['selected_plans'] = DailyPlan.objects.filter(day=selected_day).all()
        context['is_selected_today'] = selected_day == date.today()
        context['is_selected_future'] = selected_day > date.today()

        context['next_day'] = selected_day+timedelta(days=1)
        context['next_day_url'] = reverse('field.dailies', args=[context['next_day'].isoformat()])

        return context


class FieldProjectList(ProjectList):
    template_name = "field/project_list.html"


class FieldProjectView(ProjectView):
    pk_url_kwarg = 'project_pk'
    template_name = "field/project.html"

    def get_context_data(self, **kwargs):
        context = super(FieldProjectView, self).get_context_data(**kwargs)
        context['today'] = date.today()
        return context


class FieldJobList(TemplateView):
    template_name = "field/job_list.html"


class FieldJobView(DetailView):
    model = Job
    pk_url_kwarg = 'job_pk'
    template_name = "field/job.html"


def task_success_url(request, task):
    return request.GET.get('origin') or\
       reverse('field.task', args=[request.jobsite.id, request.dailyplan.url_id, task.id])


class FieldTaskView(UpdateView):
    model = Task
    pk_url_kwarg = 'task_pk'
    template_name = "field/task.html"
    form_class = CompletionForm

    def get_context_data(self, **kwargs):
        context = super(FieldTaskView, self).get_context_data(**kwargs)
        task = self.get_object()
        dailyplan = self.request.dailyplan
        context['in_current_dailyplan'] = dailyplan.id and task.daily_plans.filter(id=dailyplan.id).exists()
        return context

    def get_success_url(self):
        return task_success_url(self.request, self.object)


class FieldAssignTask(SingleObjectMixin, View):

    model = Task
    pk_url_kwarg = 'task_pk'

    def get(self, request, *args, **kwargs):
        task = self.get_object()
        dailyplan = self.request.dailyplan
        if not dailyplan.id: dailyplan.save()
        dailyplan.tasks.add(task)
        return HttpResponseRedirect(task_success_url(self.request, task))


class FieldRemoveTask(SingleObjectMixin, View):

    model = Task
    pk_url_kwarg = 'task_pk'

    def get(self, request, *args, **kwargs):
        dailyplan = self.request.dailyplan
        if dailyplan.id:
            task = self.get_object()
            daily_plan.tasks.remove(task)
        return HttpResponseRedirect(task_success_url(self.request, task))


class FieldAddSelfToDailyPlan(View):

    def get(self, request, *args, **kwargs):
        dailyplan = self.request.dailyplan
        if not dailyplan.id: dailyplan.save()

        if not TeamMember.objects.filter(plan=dailyplan, member=self.request.user).exists():
            TeamMember.objects.create(
                plan = dailyplan,
                member = self.request.user,
                is_foreman = True if kwargs['role'] == 'foreman' else False
            )

        return HttpResponseRedirect(reverse('field.dashboard'))


class FieldRemoveSelfFromDailyPlan(SingleObjectMixin, View):

    model = TeamMember

    def get(self, request, *args, **kwargs):
        self.get_object().delete()
        return HttpResponseRedirect(reverse('field.project', args=[request.jobsite.project.id]))


class FieldAssignLabor(TemplateView):

    template_name = "field/assign_labor.html"

    def get_context_data(self, **kwargs):
        context = super(FieldAssignLabor, self).get_context_data(**kwargs)
        context['workers'] = User.objects.filter(Q(is_laborer=True) | Q(is_foreman=True))
        context['assigned'] = []
        dailyplan = self.request.dailyplan
        if dailyplan.id: context['assigned'] = dailyplan.team.all()
        return context

    def post(self, request, *args, **kwargs):
        dailyplan = self.request.dailyplan
        if not dailyplan.id: dailyplan.save()

        previous_assignment = dailyplan.team.values_list('id', flat=True)

        # Add new assignments
        new_assignment = [int(id) for id in request.POST.getlist('workers')]
        for worker in new_assignment:
            if worker not in previous_assignment:
                TeamMember.objects.create(
                    plan = dailyplan,
                    member_id = worker
                )

        # Remove unchecked assignments
        for worker in previous_assignment:
            if worker not in new_assignment:
                TeamMember.objects.filter(
                    plan = dailyplan,
                    member_id = worker
                ).delete()

        return HttpResponseRedirect(reverse('field.project', args=[request.jobsite.project.id]))


class FieldToggleRole(SingleObjectMixin, View):

    model = TeamMember

    def get(self, request, *args, **kwargs):
        member = self.get_object()
        member.is_foreman = not member.is_foreman
        member.save()
        return HttpResponseRedirect(reverse('field.project', args=[request.jobsite.project.id]))