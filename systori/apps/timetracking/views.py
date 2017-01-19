import json
import datetime

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError

from systori.apps.document.views import DocumentRenderView
from systori.apps.document.type import timesheet
from systori.apps.document.models import DocumentSettings, Timesheet

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
            report=utils.get_daily_workers_report(
                self.request.company.active_workers(), self.report_period),
            **kwargs
        )

    def form_valid(self, form):
        form.save()
        # return redirect('timetracking')
        return redirect(self.request.META['HTTP_REFERER'])

    def form_invalid(self, form):
        period_form = self.period_form_class(initial={'period': timezone.now()})
        return self.render_to_response(self.get_context_data(form=form, period_form=period_form))


class WorkerReportView(PeriodFilterMixin, FormView):
    template_name = 'timetracking/user_report.html'
    form_class = forms.WorkerManualTimerForm
    period_form_class = forms.MonthPickerForm

    @cached_property
    def worker(self):
        return get_object_or_404(self.request.company.active_workers(), pk=self.kwargs['worker_id'])

    def get_form_kwargs(self):
        default_kwargs = super().get_form_kwargs()
        default_kwargs['company'] = self.request.company
        return default_kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['worker'] = self.worker
        return initial

    def get_context_data(self, **kwargs):
        timesheet = Timesheet.objects.period(self.report_period.year, self.report_period.month).\
            filter(worker_id=self.worker.id)
        return super().get_context_data(
            timesheet_worker=self.worker, timesheet=timesheet, report=utils.get_worker_monthly_report(
                self.worker, self.report_period),
            **kwargs)

    def form_valid(self, form):
        form.save()
        return redirect(self.request.META['HTTP_REFERER'])


class TimerDeleteView(DeleteView):
    model = Timer

    def get_success_url(self):
        return reverse_lazy('timetracking_worker', kwargs={'worker_id': self.object.worker.id})


class TimerDeleteSelectedDayView(ListView):
    template_name = 'timetracking/timers_confirm_delete.html'

    def get_queryset(self):
        selected_day = datetime.datetime.strptime(self.kwargs['selected_day'], '%Y-%m-%d').date()
        timers = Timer.objects.filter(date=selected_day).filter(worker_id=self.kwargs['worker_id'])

        return timers

    def get_context_data(self, **kwargs):
        timers = [timer for timer in self.get_queryset()]
        current_timer = timers[0]
        for timer in timers:
            if timer.start < current_timer.start:
                current_timer.start = timer.start
            if timer.end > current_timer.end:
                current_timer.end = timer.end
        timerange = "{:%Y-%m-%d} {:%H:%M} -> {:%H:%M}".format(current_timer.date,
                                                              timezone.localtime(current_timer.start),
                                                              timezone.localtime(current_timer.end))
        return super().get_context_data(timerange=timerange)

    def post(self, request, *args, **kwargs):
        timers = self.get_queryset()
        timers.delete()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('timetracking_worker', kwargs={'worker_id': self.kwargs['worker_id']})


class TimeSheetPDFView(DocumentRenderView):
    model = Timer

    def pdf(self):
        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        qs = Timesheet.objects.period(year, month).prefetch_related('worker')
        if self.kwargs['worker_id'] is not None:
            timesheets = qs.filter(worker_id=self.kwargs['worker_id'])
        letterhead = DocumentSettings.objects.first().timesheet_letterhead
        return timesheet.render(timesheets, letterhead)
