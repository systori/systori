from datetime import date
from django.utils.deprecation import MiddlewareMixin
from ..project.models import JobSite, DailyPlan


class FieldMiddleware(MiddlewareMixin):

    def process_view(self, request, view, args, kwargs):
        if not request.company:
            return

        if 'jobsite_pk' in kwargs:
            request.jobsite = JobSite.objects.select_related('project').get(pk=kwargs['jobsite_pk'])
            if 'dailyplan_url_id' in kwargs:
                year, month, day, plan = map(int, kwargs['dailyplan_url_id'].split('-'))
                if plan:
                    request.dailyplan = DailyPlan.objects.get(id=plan)
                else:
                    request.dailyplan = DailyPlan(day=date(year, month, day), jobsite=request.jobsite)

        if kwargs.get('selected_day'):
            request.selected_day = date(*map(int, kwargs['selected_day'].split('-')))

    def process_template_response(self, request, response):
        if request.company and hasattr(response, 'context_data'):
            if hasattr(request, 'jobsite') and 'jobsite' not in response.context_data:
                response.context_data['jobsite'] = request.jobsite
            if hasattr(request, 'dailyplan') and 'dailyplan' not in response.context_data:
                response.context_data['dailyplan'] = request.dailyplan
            if hasattr(request, 'selected_day'):
                response.context_data['selected_day'] = request.selected_day
        return response
