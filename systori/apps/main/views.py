from datetime import date, timedelta
from django.views.generic import View, TemplateView
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from systori.middleware.mobile import get_flavour
from ..project.models import Project, JobSite, DailyPlan
from ..task.models import LineItem
from ..field.views import FieldDashboard


class OfficeDashboard(TemplateView):
    template_name = "main/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(OfficeDashboard, self).get_context_data(**kwargs)
        context['flagged_lineitems'] = LineItem.objects \
            .select_related('task__job__project') \
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
        if request.user.is_authenticated:
            if not request.company:
                return HttpResponseRedirect(reverse('companies'))
            if get_flavour() == 'full' and request.worker.has_staff:
                view = OfficeDashboard.as_view()
            else:
                view = FieldDashboard.as_view()
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('login'))


class DayBasedOverviewView(TemplateView):
    template_name = "main/day_based_overview.html"

    def get_context_data(self, **kwargs):
        context = super(DayBasedOverviewView, self).get_context_data(**kwargs)

        selected_day = date(*map(int, kwargs['selected_day'].split('-'))) if kwargs['selected_day'] else date.today()

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
