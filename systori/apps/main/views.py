import json
from datetime import date, timedelta
from django.views.generic import View, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.views import login
from django_mobile import get_flavour
from django.conf import settings
from django.template import defaultfilters
from django.core.urlresolvers import reverse

from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from ..project.models import Project, JobSite, DailyPlan
from ..task.models import LineItem
from ..field.views import FieldDashboard



class OfficeDashboard(TemplateView):
    template_name = "main/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(OfficeDashboard, self).get_context_data(**kwargs)
        context['flagged_lineitems'] = LineItem.objects \
            .select_related('taskinstance__task__taskgroup__job__project') \
            .filter(is_flagged=True) \
            .all()
        context['job_sites'] = JobSite.objects \
            .select_related('project') \
            .exclude(project__phase=Project.WARRANTY) \
            .exclude(project__phase=Project.FINISHED) \
            .exclude(latitude=None).exclude(longitude=None) \
            .all()
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context


class IndexView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if get_flavour() == 'full' and request.access.has_staff:
                view = OfficeDashboard.as_view()
            else:
                view = FieldDashboard.as_view()
            return view(request, *args, **kwargs)
        else:
            return login(request, template_name="user/login.html")


class DayBasedOverviewView(TemplateView):
    template_name = "main/day_based_overview.html"

    def get_context_data(self, **kwargs):
        context = super(DayBasedOverviewView, self).get_context_data(**kwargs)

        if not hasattr(self.request, 'selected_day'):
            self.request.selected_day = date.today()
        selected_day = self.request.selected_day

        context['today'] = date.today()
        context['previous_day'] = selected_day - timedelta(days=1)
        context['next_day'] = selected_day + timedelta(days=1)

        context['previous_day_url'] = reverse('day_based_overview', args=[context['previous_day'].isoformat()])
        context['today_url'] = reverse('day_based_overview', args=[date.today().isoformat()])
        context['next_day_url'] = reverse('day_based_overview', args=[context['next_day'].isoformat()])

        context['selected_day'] = selected_day
        context['selected_plans'] = DailyPlan.objects.filter(day=selected_day).order_by('jobsite__project_id').all()
        context['is_selected_today'] = selected_day == date.today()
        context['is_selected_future'] = selected_day > date.today()

        return context


class DailyPlanView(SingleObjectMixin, View):
    model = DailyPlan

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        template = get_template("main/dailyplan_template.html")
        context = Context({'object' : self.object})
        rendered = template.render(context).encode('utf-8')
        return HttpResponse(rendered)


class DailyPlansPerDayJson(View):

    def get(self, request, *args, **kwargs):
        selected_day = request.selected_day

        data = {}
        data['selected_date'] = []
        data['selected_date'].append(defaultfilters.date(selected_day, 'Y-m-d'))
        data['selected_date'].append(defaultfilters.date(selected_day, 'l d. M Y'))
        data['dailyplan_ids'] = []
        for dailyplan in DailyPlan.objects.filter(day=selected_day).order_by('jobsite__project_id').all():
            data['dailyplan_ids'].append(dailyplan.id)

        return HttpResponse(json.dumps(data), content_type='application/json')