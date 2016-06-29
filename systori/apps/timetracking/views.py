import json

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from . import utils
from . import forms


User = get_user_model()


class HomeView(FormView):
    template_name = 'timetracking/home.html'
    form_class = forms.ManualTimerForm

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
    form_class = forms.UserManualTimerForm

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
            **kwargs
        )

    def form_valid(self, form):
        form.save()
        return redirect('timetracking_user', self.user.pk)

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        period_form = forms.MonthPickerForm(request.GET, initial={'period': timezone.now()})
        if period_form.is_valid():
            report_period = period_form.cleaned_data['period']
        else:
            report_period = timezone.now()
        return self.render_to_response(self.get_context_data(
            form=form, report_period=report_period,
            report=utils.get_user_monthly_report(self.user, report_period),
            period_form=period_form
        ))
