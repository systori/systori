import json

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from . import utils
from .forms import SuperuserTimerForm


User = get_user_model()


class HomeView(TemplateView):
    template_name = 'timetracking/timetracking.html'

    # def get_context_data(self, **kwargs):
    #     report = list(utils.get_today_report(User.objects.all()))
    #     context = {
    #         'report': report
    #     }
    #     context.update(kwargs)
    #     if 'formset' not in context:
    #         context['formset'] = embed_forms(self.request, report)
    #     return context

    def get(self, request, *args, **kwargs):
        report = list(utils.get_today_report(User.objects.all()))
        form = SuperuserTimerForm()
        context = {
            'report': report,
            'form': form
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        report = list(utils.get_today_report(User.objects.all()))
        form = SuperuserTimerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('timetracking')
        else:
            return self.render_to_response({
                'report': report,
                'form': form
            })
