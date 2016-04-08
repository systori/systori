import json

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from . import utils


User = get_user_model()


class HomeView(TemplateView):
    template_name = 'timetracking/timetracking.html'

    def get_context_data(self, **kwargs):
        report = utils.get_today_report(User.objects.all())
        return {
            'report': report
        }
