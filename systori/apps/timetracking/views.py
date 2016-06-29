import json

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from . import utils
from .forms import ManualTimerForm, UserManualTimerForm


User = get_user_model()


class HomeView(FormView):
    template_name = 'timetracking/home.html'
    form_class = ManualTimerForm

    def get_form_kwargs(self):
        default_kwargs = super().get_form_kwargs()
        default_kwargs['company'] = self.request.company
        return default_kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            report=utils.get_daily_users_report(self.request.company.active_users()),
            **kwargs
        )

    def form_valid(self, form):
        form.save()
        return redirect('timetracking')


class UserReportView(FormView):
    template_name = 'timetracking/user_report.html'
    form_class = UserManualTimerForm

    @cached_property
    def user(self):
        return get_object_or_404(User, pk=self.kwargs['user_id'])

    def get_form_kwargs(self):
        default_kwargs = super().get_form_kwargs()
        default_kwargs['company'] = self.request.company
        return default_kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.user
        return initial

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            user=self.user,
            report=utils.get_user_monthly_report(self.user),
            **kwargs
        )

    def form_valid(self, form):
        form.save()
        return redirect('timetracking_user', self.user.pk)
