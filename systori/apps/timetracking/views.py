import json
import datetime

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError

from systori.apps.document.views import DocumentRenderView
from systori.apps.document.type import timesheet
from systori.apps.document.models import DocumentSettings

from . import utils
from . import forms
from .models import Timer

class PeriodFilterMixin:
    report_period = None

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        period_form = self.period_form_class(request.GET, initial={'period': timezone.now()})
        if period_form.is_valid():
            self.report_period = period_form.cleaned_data['period']
        else:
            self.report_period = timezone.now().date()
            period_form = self.period_form_class(initial={'period': timezone.now()})

        return self.render_to_response(self.get_context_data(
            form=form, report_period=self.report_period,
            period_form=period_form
        ))


class HomeView(PeriodFilterMixin, FormView):
    template_name = 'timetracking/home.html'
    form_class = forms.ManualTimerForm
    period_form_class = forms.DayPickerForm

    def get_form_kwargs(self):
        default_kwargs = super().get_form_kwargs()
        default_kwargs['company'] = self.request.company
        return default_kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            report=utils.get_daily_users_report(
                self.request.company.active_users(), self.report_period),
            **kwargs
        )

    def form_valid(self, form):
        form.save()
        # return redirect('timetracking')
        return redirect(self.request.META['HTTP_REFERER'])

    def form_invalid(self, form):
        period_form = self.period_form_class(initial={'period': timezone.now()})
        return self.render_to_response(self.get_context_data(form=form, period_form=period_form))


class UserReportView(PeriodFilterMixin, FormView):
    template_name = 'timetracking/user_report.html'
    form_class = forms.UserManualTimerForm
    period_form_class = forms.MonthPickerForm

    @cached_property
    def user(self):
        return get_object_or_404(self.request.company.active_users(), pk=self.kwargs['user_id'])

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
            user=self.user, report=utils.get_user_monthly_report(
                self.user, self.report_period),
            **kwargs)

    def form_valid(self, form):
        form.save()
        # return redirect('timetracking_user', self.user.pk)
        return redirect(self.request.META['HTTP_REFERER'])


class TimeSheetPDFView(DocumentRenderView):
    model = Timer

    def pdf(self):
        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        qs = Timer.objects.filter_month(year, month).prefetch_related('user')
        if self.kwargs['user_id'] is not None:
            qs = qs.filter(user_id=self.kwargs['user_id'])
        letterhead = DocumentSettings.objects.first().timetracking_letterhead
        return timesheet.render(qs, letterhead, datetime.date(year, month, 1))
