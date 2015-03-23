from datetime import timedelta, date
from calendar import LocaleHTMLCalendar, month_name
from itertools import groupby
from django.http import HttpResponseRedirect
from django.db.models import Q, Count
from django.utils.formats import to_locale, get_language
from django.views.generic import View, DetailView, ListView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse
from ..user.models import User
from ..project.models import Project, DailyPlan, JobSite, TeamMember
from ..task.models import Job, Task, ProgressReport
from .forms import CompletionForm
from .utils import find_next_workday, days_ago


def _origin_success_url(request, alternate):
    return request.GET.get('origin') or\
           request.POST.get('origin') or\
           alternate

def project_success_url(request):
    return _origin_success_url(request,
            reverse('field.project', args=[request.jobsite.project.id]))

def task_success_url(request, task):
    return _origin_success_url(request,
            reverse('field.dailyplan.task', args=[request.jobsite.id, request.dailyplan.url_id, task.id]))

def dashboard_success_url(request):
    return _origin_success_url(request,
            reverse('field.dashboard'))


def delete_when_empty(dailyplan):
    if dailyplan.tasks.count() == 0 and\
       dailyplan.users.count() == 0:
        dailyplan.delete()
        return True
    return False

class FieldDashboard(TemplateView):
    template_name = "field/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(FieldDashboard, self).get_context_data(**kwargs)

        context['todays_plans'] = self.request.user.todays_plans.all()

        context['previous_plans'] = self.request.user.dailyplans\
            .filter(day__gt=days_ago(5))\
            .exclude(day=date.today()).all()

        return context


class FieldPlanning(TemplateView):
    template_name = "field/planning.html"

    def get_context_data(self, **kwargs):
        context = super(FieldPlanning, self).get_context_data(**kwargs)

        if not hasattr(self.request, 'selected_day'):
            self.request.selected_day = date.today()
        selected_day = self.request.selected_day

        context['today'] = date.today()
        context['previous_day'] = selected_day-timedelta(days=1)
        context['next_day'] = selected_day+timedelta(days=1)

        context['previous_day_url'] = reverse('field.planning', args=[context['previous_day'].isoformat()])
        context['today_url'] = reverse('field.planning', args=[date.today().isoformat()])
        context['next_day_url'] = reverse('field.planning', args=[context['next_day'].isoformat()])

        context['selected_day'] = selected_day
        context['selected_plans'] = DailyPlan.objects.filter(day=selected_day).order_by('jobsite__project_id').all()
        context['is_selected_today'] = selected_day == date.today()
        context['is_selected_future'] = selected_day > date.today()

        return context


class FieldProjectList(ListView):
    model = Project
    template_name = "field/project_list.html"

    def get_queryset(self):
        return self.model.objects.without_template()


class FieldProjectView(DetailView):
    model = Project
    pk_url_kwarg = 'project_pk'
    template_name = "field/project.html"

    def get_context_data(self, **kwargs):
        context = super(FieldProjectView, self).get_context_data(**kwargs)

        if not hasattr(self.request, 'selected_day'):
            self.request.selected_day = find_next_workday(date.today())
        selected_day = self.request.selected_day

        project = self.get_object()

        daily_plans = DailyPlan.objects\
                        .filter(jobsite__project=project)\
                        .filter(day__lte=selected_day)\
                        .filter(day__gte=selected_day-timedelta(days=3))\
                        .all()

        grouped_by_days = []
        for day, plans in groupby(daily_plans, lambda o: o.day):
            grouped_by_days.append((day, list(plans)))

        context['first_daily_plan'] = daily_plans.first()
        context['latest_daily_plan'] = DailyPlan.objects.filter(jobsite__project=project).first()
        context['daily_plans'] = grouped_by_days
        context['today'] = date.today()

        return context


class FieldHTMLCalendar(LocaleHTMLCalendar):
    def __init__(self, project, year, month, start_date, end_date):
        super(FieldHTMLCalendar, self).__init__(locale=(to_locale(get_language()), 'utf-8'))
        self.project = project
        self.year = year
        self.month = month
        self.today = date.today()

        plans = DailyPlan.objects\
                .filter(jobsite__project=project,
                        day__lt=end_date,
                        day__gt=start_date
                ).values('day').annotate(plans=Count('day'))

        self.plans = dict([(p['day'],p['plans']) for p in plans])

    def render(self):
        return self.formatmonth(self.year, self.month)

    def formatmonthname(self, theyear, themonth, withyear=True): return ''

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            day_date = date(self.year, self.month, day)
            return '<td class="%s"><a href="%s">%d <span class="dailyplan-count">%s</span></a></td>' % (
                        self.cssclasses[weekday] +\
                         (' today' if self.today==day_date else '') +\
                         (' scheduled' if day_date in self.plans else ''),
                        reverse('field.project', args=[self.project.id, day_date.isoformat()]),
                        day, self.plans.get(day_date, '')
                    )


class FieldProjectCalendar(TemplateView):
    template_name = "field/calendar.html"

    def get_context_data(self, **kwargs):
        context = super(FieldProjectCalendar, self).get_context_data(**kwargs)

        project = self.request.project
        day = self.request.selected_day

        previous = date(day.year, day.month, 1)-timedelta(days=1)
        context['previous_month'] = date(previous.year, previous.month, 1)

        next = date(day.year, day.month, 25)+timedelta(days=10)
        context['next_month'] = date(next.year, next.month, 1)

        context['calendar'] = FieldHTMLCalendar(project, day.year, day.month,
                                previous, context['next_month']).render()

        return context


class FieldGenerateDailyPlans(View):

    def get(self, request, *args, **kwargs):

        project = request.project
        selected_day = request.selected_day
        other_day = date(*map(int, kwargs['other_day'].split('-')))

        really_crappy_task_picking_algorithm = Task.objects\
            .filter(taskgroup__job__project=project)\
            .order_by('id')

        for oldplan in DailyPlan.objects.filter(jobsite__project=project, day=other_day):

            newplan = DailyPlan.objects.create(jobsite=oldplan.jobsite, day=selected_day)

            for task in oldplan.tasks.all():
                newplan.tasks.add(task)

            for oldmember in oldplan.workers.all():
                TeamMember.objects.create(
                    dailyplan=newplan,
                    user=oldmember.user,
                    is_foreman=oldmember.is_foreman
                )

        return HttpResponseRedirect(reverse('field.project', args=[project.id, selected_day.isoformat()]))


class FieldPickJobSite(TemplateView):
    template_name = "field/job_list.html"


class FieldJobList(TemplateView):
    template_name = "field/job_list.html"

    def dispatch(self, request, *args, **kwargs):
        if request.jobsite.project.jobs.count() == 1:
            kwargs['job_pk'] = request.jobsite.project.jobs.first().id
            return FieldJobView.as_view()(request, *args, **kwargs)
        else:
            return super(FieldJobList, self).dispatch(request, *args, **kwargs)


class FieldJobView(DetailView):
    model = Job
    pk_url_kwarg = 'job_pk'
    template_name = "field/job.html"


class FieldTaskView(UpdateView):
    model = Task
    pk_url_kwarg = 'task_pk'
    template_name = "field/task.html"
    form_class = CompletionForm

    def get_context_data(self, **kwargs):
        context = super(FieldTaskView, self).get_context_data(**kwargs)
        task = self.get_object()
        dailyplan = self.request.dailyplan
        context['in_current_dailyplan'] = dailyplan.id and task.dailyplans.filter(id=dailyplan.id).exists()
        return context

    def form_valid(self, form):

        redirect = super(FieldTaskView, self).form_valid(form)

        if 'complete' in form.changed_data or form.cleaned_data['comment']:
            ProgressReport.objects.create(
                user = self.request.user,
                task = self.object,
                complete = self.object.complete,
                comment = form.cleaned_data['comment']
            )

        return redirect

    def get_success_url(self):
        return task_success_url(self.request, self.object)


class FieldAddTask(SingleObjectMixin, View):

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
            dailyplan.tasks.remove(task)

        if delete_when_empty(dailyplan):
            return HttpResponseRedirect(project_success_url(request))
        else:
            return HttpResponseRedirect(task_success_url(self.request, task))


class FieldAddSelfToDailyPlan(View):

    def get(self, request, *args, **kwargs):

        dailyplan = self.request.dailyplan
        if not dailyplan.id: dailyplan.save()

        already_assigned =\
         TeamMember.objects.filter(dailyplan=dailyplan, user=self.request.user).exists()

        if not already_assigned:
            TeamMember.objects.create(
                dailyplan = dailyplan,
                user = request.user,
                is_foreman = True if kwargs['role'] == 'foreman' else False
            )

        delete_when_empty(dailyplan)

        return HttpResponseRedirect(dashboard_success_url(request))


class FieldRemoveSelfFromDailyPlan(View):

    def get(self, request, *args, **kwargs):

        TeamMember.objects.filter(
            dailyplan = request.dailyplan,
            user = request.user
        ).delete()

        delete_when_empty(request.dailyplan)

        return HttpResponseRedirect(dashboard_success_url(request))


class FieldAssignLabor(TemplateView):

    template_name = "field/assign_labor.html"

    def get_context_data(self, **kwargs):
        context = super(FieldAssignLabor, self).get_context_data(**kwargs)
        context['workers'] = User.objects\
                                .filter(Q(is_laborer=True) | Q(is_foreman=True))\
                                .annotate(plan_count=Count('dailyplans'))\
                                .order_by('plan_count', 'username')
        context['assigned'] = []
        dailyplan = self.request.dailyplan
        if dailyplan.id: context['assigned'] = dailyplan.users.all()
        return context

    def post(self, request, *args, **kwargs):

        dailyplan = self.request.dailyplan


        new_assignments = [int(id) for id in request.POST.getlist('workers')]

        redirect = project_success_url(request)
        if not dailyplan.id:
            origin = request.GET.get('origin') or request.POST.get('origin')
            redirect = reverse('field.dailyplan.assign-tasks',
                           args=[dailyplan.jobsite.id, dailyplan.url_id])+\
                           '?origin='+origin if origin else ''

            if not new_assignments:
                return HttpResponseRedirect(redirect)

            else:
                dailyplan.save()

        previous_assignments = dailyplan.users.values_list('id', flat=True)

        # Add new assignments
        for worker in new_assignments:
            if worker not in previous_assignments:
                TeamMember.objects.create(
                    dailyplan = dailyplan,
                    user_id = worker
                )

        # Remove unchecked assignments
        for worker in previous_assignments:
            if worker not in new_assignments:
                TeamMember.objects.filter(
                    dailyplan = dailyplan,
                    user_id = worker
                ).delete()

        delete_when_empty(dailyplan)

        return HttpResponseRedirect(redirect)


class FieldToggleRole(SingleObjectMixin, View):

    model = TeamMember

    def get(self, request, *args, **kwargs):
        member = self.get_object()
        member.is_foreman = not member.is_foreman
        member.save()
        return HttpResponseRedirect(project_success_url(request))