import json
from datetime import timedelta, date
from calendar import LocaleHTMLCalendar, month_name
from itertools import groupby

from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q, Count, Prefetch
from django.utils.http import urlquote
from django.utils.formats import to_locale, get_language
from django.views.generic import View, DetailView, ListView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse

from ..company.models import Worker
from ..project.models import Project, DailyPlan, EquipmentAssignment, TeamMember
from ..task.models import Job, Group, Task, ProgressReport
from ..equipment.models import Equipment
from ..timetracking import utils as timetracking_utils
from .forms import CompletionForm, DailyPlanNoteForm
from .utils import find_next_workday, days_ago


def _origin_success_url(request, alternate):
    return request.GET.get('origin') or \
           request.POST.get('origin') or \
           alternate


def project_success_url(request):
    return _origin_success_url(request,
           reverse('field.project', args=[request.jobsite.project.id]))


def task_success_url(request, task):
    if request.jobsite.project.jobs.count() > 1:
        return reverse('field.dailyplan.group',
                       args=[request.jobsite.id, request.dailyplan.url_id, task.job.id])
    else:
        return _origin_success_url(request,
                                   reverse('field.dailyplan.task',
                                           args=[request.jobsite.id, request.dailyplan.url_id, task.id]))


def equipment_success_url(request, equipment):
    return _origin_success_url(request,
                               reverse('field.dailyplan.equipment',
                                       args=[request.jobsite.id, request.dailyplan.url_id, equipment.id]))


def dashboard_success_url(request):
    return _origin_success_url(request,
                               reverse('field.dashboard'))


def delete_when_empty(dailyplan):
    if dailyplan.tasks.count() == 0 and \
                    dailyplan.workers.count() == 0 and \
                    dailyplan.equipment.count() == 0:
        dailyplan.delete()
        return True
    return False


def daily_plan_objects():
    return DailyPlan.objects \
        .prefetch_related("jobsite__project__jobsites") \
        .prefetch_related(Prefetch("assigned_equipment", queryset=EquipmentAssignment.objects.select_related("equipment"))) \
        .prefetch_related("tasks")


class FieldDashboard(TemplateView):
    template_name = "field/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(FieldDashboard, self).get_context_data(**kwargs)
        worker = self.request.worker
        if worker.is_fake:
            todays_plans = previous_plans = []
        else:
            todays_plans = self.request.worker.todays_plans.all()
            previous_plans = self.request.worker.dailyplans \
                .filter(day__gt=days_ago(5)) \
                .exclude(day=date.today()).all()

        context.update({
            'todays_plans': todays_plans,
            'previous_plans': previous_plans,
            'timetracking_report': timetracking_utils.get_worker_dashboard_report(self.request.worker),
            'timetracking_timer_duration': timetracking_utils.get_running_timer_duration(self.request.worker)
        })

        return context


class FieldPlanning(TemplateView):
    template_name = "field/planning.html"

    def get_context_data(self, **kwargs):
        context = super(FieldPlanning, self).get_context_data(**kwargs)

        if not hasattr(self.request, 'selected_day'):
            self.request.selected_day = date.today()
        selected_day = self.request.selected_day

        context['today'] = date.today()
        context['previous_day'] = selected_day - timedelta(days=1)
        context['next_day'] = selected_day + timedelta(days=1)

        context['previous_day_url'] = reverse('field.planning', args=[context['previous_day'].isoformat()])
        context['today_url'] = reverse('field.planning', args=[date.today().isoformat()])
        context['next_day_url'] = reverse('field.planning', args=[context['next_day'].isoformat()])

        context['selected_day'] = selected_day
        context['selected_plans'] = daily_plan_objects() \
            .filter(day=selected_day) \
            .order_by('jobsite__project_id') \
            .all()
        context['is_selected_today'] = selected_day == date.today()
        context['is_selected_future'] = selected_day > date.today()

        context['latest_daily_plan'] = DailyPlan.objects.first()
        context['latest_days_with_plans'] = DailyPlan.objects.values('day').distinct()[:5]

        return context


class FieldProjectList(ListView):
    model = Project
    template_name = "field/project_list.html"

    def get_queryset(self):
        return Project.objects \
            .without_template() \
            .filter(phase__in=[Project.PLANNING, Project.EXECUTING]) \
            .order_by('id')


class FieldProjectView(DetailView):
    model = Project
    pk_url_kwarg = 'project_pk'
    template_name = "field/project.html"

    def get_object(self):
        return self.request.project

    def get_context_data(self, **kwargs):
        context = super(FieldProjectView, self).get_context_data(**kwargs)

        if not hasattr(self.request, 'selected_day'):
            self.request.selected_day = find_next_workday(date.today())
        selected_day = self.request.selected_day

        project = self.object

        daily_plans = daily_plan_objects() \
            .filter(jobsite__in=project.jobsites.all()) \
            .filter(day__lte=selected_day) \
            .filter(day__gte=selected_day - timedelta(days=3)) \
            .all()

        grouped_by_days = []
        for day, plans in groupby(daily_plans, lambda o: o.day):
            grouped_by_days.append((day, list(plans)))

        # make sure the first record is always the selected_day even if none exists
        if not grouped_by_days or grouped_by_days[0][0] != selected_day:
            grouped_by_days.insert(0, (selected_day, []))

        context['daily_plans'] = grouped_by_days
        context['latest_daily_plan'] = daily_plan_objects().filter(jobsite__in=project.jobsites.all()).first()
        context['today'] = date.today()

        return context


class FieldHTMLCalendar(LocaleHTMLCalendar):
    def __init__(self, project, year, month, start_date, end_date, make_link):
        super(FieldHTMLCalendar, self).__init__(locale=(to_locale(get_language()), 'utf-8'))
        self.project = project
        self.year = year
        self.month = month
        self.today = date.today()
        self.make_link = make_link

        plans = DailyPlan.objects \
            .filter(jobsite__project=project,
                    day__lt=end_date,
                    day__gt=start_date
                    ).values('day').annotate(plans=Count('day'))

        self.plans = dict([(p['day'], p['plans']) for p in plans])

    def render(self):
        return self.formatmonth(self.year, self.month)

    def formatmonthname(self, theyear, themonth, withyear=True):
        return ''

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            day_date = date(self.year, self.month, day)
            return '<td class="%s"><a href="%s">%d <span class="dailyplan-count">%s</span></a></td>' % (
                self.cssclasses[weekday] + \
                (' today' if self.today == day_date else '') + \
                (' scheduled' if day_date in self.plans else ''),
                self.make_link(day_date),
                day, self.plans.get(day_date, '')
            )


class FieldProjectCalendar(TemplateView):
    template_name = "field/calendar.html"

    def get_context_data(self, **kwargs):
        context = super(FieldProjectCalendar, self).get_context_data(**kwargs)

        project = self.request.project
        day = self.request.selected_day

        previous = date(day.year, day.month, 1) - timedelta(days=1)
        context['previous_month'] = date(previous.year, previous.month, 1)

        next = date(day.year, day.month, 25) + timedelta(days=10)
        context['next_month'] = date(next.year, next.month, 1)

        context['calendar'] = FieldHTMLCalendar(
            project, day.year, day.month,
            previous, context['next_month'],
            lambda day_date:
                reverse('field.project', args=[project.id, day_date.isoformat()]) +
                '?copy_source_date=' + self.request.GET.get('copy_source_date','')
        ).render()

        return context


class FieldCopyPasteDailyPlans(View):

    def get(self, request, *args, **kwargs):

        project = request.project
        selected_day = request.selected_day
        other_day = date(*map(int, kwargs['source_day'].split('-')))

        for oldplan in DailyPlan.objects.filter(jobsite__project=project, day=other_day):

            newplan = DailyPlan.objects.create(jobsite=oldplan.jobsite, day=selected_day, notes=oldplan.notes)

            for oldmember in oldplan.members.all():
                TeamMember.objects.create(
                    dailyplan=newplan,
                    worker=oldmember.worker,
                    is_foreman=oldmember.is_foreman
                )

        return HttpResponseRedirect(reverse('field.project', args=[project.id, selected_day.isoformat()]))


class FieldGenerateAllDailyPlans(View):

    def get(self, request, source_day, *args, **kwargs):

        selected_day = request.selected_day

        for oldplan in DailyPlan.objects.filter(day=source_day):

            newplan = DailyPlan.objects.create(jobsite=oldplan.jobsite,
                                               day=selected_day,
                                               notes=oldplan.notes)

            for oldmember in oldplan.members.all():
                TeamMember.objects.create(
                    dailyplan=newplan,
                    worker=oldmember.worker,
                    is_foreman=oldmember.is_foreman
                )

            for oldequipment in oldplan.assigned_equipment.all():
                EquipmentAssignment.objects.create(
                    dailyplan=newplan,
                    equipment_id=oldequipment.equipment_id
                )

        return HttpResponseRedirect(reverse('field.planning', args=[selected_day.isoformat()]))


class FieldPickJobSite(TemplateView):
    template_name = "field/jobsite_list.html"


class FieldGroupView(DetailView):
    model = Group
    pk_url_kwarg = 'group_pk'
    template_name = 'field/group.html'
    context_object_name = 'parent'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_parent_project'] = isinstance(self.object, Project)
        context['is_parent_job'] = isinstance(self.object, Group) and self.object.is_root

        if context['is_parent_project']:
            depth = -1
            groups = self.object.jobs
        else:
            depth = self.object.depth
            groups = self.object.groups

        structure = self.request.jobsite.project.structure

        context.update({
            'parent_has_subgroups': False,
            'parent_has_tasks': False,
            'subgroups_have_subgroups': False,
            'subgroups_have_tasks': False,
            'groups': None,
            'tasks': None
        })

        if structure.is_valid_depth(depth+1):
            context['parent_has_subgroups'] = True
            if structure.is_valid_depth(depth+2):
                context['subgroups_have_subgroups'] = True
                context['groups'] = groups.prefetch_related('groups')
            else:
                context['subgroups_have_tasks'] = True
                context['groups'] = groups.prefetch_related('tasks__progressreports')
        else:
            context['parent_has_tasks'] = True
            context['tasks'] = self.object.tasks.prefetch_related('progressreports')

        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            return super().get_object()
        else:
            return self.request.jobsite.project


class FieldTaskView(UpdateView):
    model = Task
    pk_url_kwarg = 'task_pk'
    template_name = 'field/task.html'
    form_class = CompletionForm

    def get_queryset(self):
        return super().get_queryset()\
            .prefetch_related('job__project') \
            .prefetch_related('lineitems') \
            .prefetch_related('dailyplans') \
            .prefetch_related('progressreports__worker__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        dailyplan = self.request.dailyplan
        context['in_current_dailyplan'] = dailyplan.id and dailyplan in task.dailyplans.all()
        return context

    def form_valid(self, form):
        redirect = super().form_valid(form)

        complete_filled = 'complete' in form.changed_data

        if complete_filled:
            self.assign_task_to_user_dailyplan(self.object)

        if complete_filled or form.cleaned_data['comment']:
            ProgressReport.objects.create(
                worker=self.request.worker,
                task=self.object,
                complete=self.object.complete,
                comment=form.cleaned_data['comment']
            )

        return redirect

    def assign_task_to_user_dailyplan(self, task):
        dailyplan = self.request.dailyplan
        worker = self.request.worker
        dailyplan_assigned = dailyplan.id and dailyplan.members.filter(worker=worker).exists()
        if dailyplan_assigned and not task.dailyplans.filter(id=dailyplan.id).exists():
            task.dailyplans.add(dailyplan)

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

        already_assigned = TeamMember.objects.filter(
            dailyplan=dailyplan, worker=self.request.worker).exists()

        if not already_assigned:
            TeamMember.objects.create(
                dailyplan=dailyplan,
                worker=request.worker,
                is_foreman=True if kwargs['role'] == 'foreman' else False
            )

        delete_when_empty(dailyplan)

        return HttpResponseRedirect(dashboard_success_url(request))


class FieldRemoveSelfFromDailyPlan(View):
    def get(self, request, *args, **kwargs):
        TeamMember.objects.filter(
            dailyplan=request.dailyplan,
            worker=request.worker
        ).delete()

        delete_when_empty(request.dailyplan)

        return HttpResponseRedirect(dashboard_success_url(request))


class FieldAssignLabor(TemplateView):
    template_name = "field/assign_labor.html"

    def get_context_data(self, **kwargs):
        context = super(FieldAssignLabor, self).get_context_data(**kwargs)

        dailyplan = self.request.dailyplan

        assigned = []
        if dailyplan.id:
            assigned = dailyplan.workers.all()

        plan_count = """
            SELECT
                count(*)
            FROM
                project_teammember
                INNER JOIN project_dailyplan ON (project_teammember.dailyplan_id = project_dailyplan.id)
            WHERE
                project_teammember.worker_id = company_worker.id AND
                project_dailyplan.day = %s
        """
        params = (dailyplan.day,)
        workers = Worker.objects \
            .prefetch_related("user") \
            .filter(company=self.request.company) \
            .filter(is_active=True) \
            .filter(Q(is_laborer=True) | Q(is_foreman=True)) \
            .extra(select={'plan_count': plan_count}, select_params=params) \
            .order_by('plan_count', 'user__first_name') \
            .all()

        assigned_workers = []
        available_workers = []
        for worker in workers:
            worker.assigned = worker in assigned
            if worker.assigned:
                assigned_workers.append(worker)
            else:
                available_workers.append(worker)

        context['workers'] = assigned_workers + available_workers
        return context

    def post(self, request, *args, **kwargs):

        dailyplan = self.request.dailyplan

        new_assignments = [int(id) for id in request.POST.getlist('workers')]

        redirect = project_success_url(request)
        if not dailyplan.id:

            if new_assignments:
                dailyplan.save()

            if not new_assignments:
                return HttpResponseRedirect(redirect)

        previous_assignments = dailyplan.workers.values_list('id', flat=True)

        # Add new assignments
        for worker in new_assignments:
            if worker not in previous_assignments:
                TeamMember.objects.create(
                    dailyplan=dailyplan,
                    worker_id=worker
                )

        # Remove unchecked assignments
        for worker in previous_assignments:
            if worker not in new_assignments:
                TeamMember.objects.filter(
                    dailyplan=dailyplan,
                    worker_id=worker
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


class FieldMemberRemove(SingleObjectMixin, View):
    model = TeamMember

    def get(self, request, *args, **kwargs):
        self.get_object().delete()

        delete_when_empty(request.dailyplan)

        return HttpResponseRedirect(project_success_url(request))


class FieldDailyPlanNotes(UpdateView):
    model = DailyPlan
    form_class = DailyPlanNoteForm

    def get_success_url(self):
        return dashboard_success_url(self.request)


class FieldPlanningToggle(View):
    def get(self, request, *args, **kwargs):
        toggle = 'is_planning_' + kwargs['toggle']
        request.session[toggle] = not request.session.get(toggle, False)
        return HttpResponseRedirect(reverse('field.planning', args=[self.request.selected_day.isoformat()]))


class FieldAssignEquipment(TemplateView):
    template_name = "field/assign_equipment.html"

    def get_context_data(self, **kwargs):
        context = super(FieldAssignEquipment, self).get_context_data(**kwargs)
        context['equipment_list'] = Equipment.objects \
            .filter(active=True) \
            .annotate(plan_count=Count('dailyplans')) \
            .order_by('plan_count', 'name')
        context['assigned'] = []
        dailyplan = self.request.dailyplan
        if dailyplan.id: context['assigned'] = dailyplan.equipment.all()
        return context

    def post(self, request, *args, **kwargs):

        dailyplan = self.request.dailyplan

        new_assignments = [int(id) for id in request.POST.getlist('equipment_list')]

        redirect = project_success_url(request)
        if not dailyplan.id:

            if new_assignments:
                dailyplan.save()

            origin = urlquote(_origin_success_url(request, ''))

            redirect = reverse('field.dailyplan.assign-equipment',
                               args=[dailyplan.jobsite.id, dailyplan.url_id]) + \
                               '?origin=' + origin

            if not new_assignments:
                return HttpResponseRedirect(redirect)

        previous_assignments = dailyplan.equipment.values_list('id', flat=True)

        # Add new assignments
        for equipment in new_assignments:
            if equipment not in previous_assignments:
                EquipmentAssignment.objects.create(
                    dailyplan=dailyplan,
                    equipment_id=equipment
                )

        # Remove unchecked assignments
        for equipment in previous_assignments:
            if equipment not in new_assignments:
                EquipmentAssignment.objects.filter(
                    dailyplan=dailyplan,
                    equipment_id=equipment
                ).delete()

        delete_when_empty(dailyplan)

        return HttpResponseRedirect(redirect)


class FieldPaste(View):
    def post(self, request, *args, **kwargs):
        dailyplan = self.request.dailyplan
        clipboard = json.loads(request.body.decode('utf-8'))
        member_ids = clipboard.get('workers', [])
        members = TeamMember.objects.filter(id__in=member_ids)
        members.update(dailyplan=dailyplan)
        equipment_ids = clipboard.get('equipment', [])
        equipment = EquipmentAssignment.objects.filter(id__in=equipment_ids)
        equipment.update(dailyplan=dailyplan)
        plans = clipboard.get('empty-plans', [])
        for plan in daily_plan_objects().filter(id__in=plans):
            delete_when_empty(plan)
        return HttpResponse("OK")


class FieldEquipmentList(ListView):
    model = Equipment
    template_name = "field/equipment_list.html"
    queryset = Equipment.objects.filter(active=True)