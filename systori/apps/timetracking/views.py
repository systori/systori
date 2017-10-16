import datetime

from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import BaseCreateView, DeleteView
from django.views.generic.list import ListView
from django.utils import timezone
from django.utils.functional import cached_property

from . import forms
from .models import Timer


class PeriodFilterMixin(TemplateView):
    period_form_class = None

    def get_context_data(self, **kwargs):
        report_period = timezone.localdate()
        period_form = self.period_form_class(self.request.GET)
        if period_form.is_valid():
            report_period = period_form.cleaned_data['period']
        else:
            period_form = self.period_form_class(initial={'period': report_period})
        return super().get_context_data(
            report_period=report_period,
            period_form=period_form,
            **kwargs
        )


class HomeView(BaseCreateView, PeriodFilterMixin):
    template_name = 'timetracking/home.html'
    form_class = forms.ManualTimerForm
    period_form_class = forms.DayPickerForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.company
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report'] = Timer.objects.get_daily_workers_report(context['report_period'])
        return context

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class VacationScheduleView(ListView):
    template_name = 'timetracking/vacation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Timer.objects.get_vacation_schedule(timezone.localdate())


class WorkerReportView(BaseCreateView, PeriodFilterMixin):
    template_name = 'timetracking/user_report.html'
    form_class = forms.WorkerManualTimerForm
    period_form_class = forms.MonthPickerForm

    @cached_property
    def worker(self):
        return get_object_or_404(self.request.company.tracked_workers(), pk=self.kwargs['worker_id'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.company
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['worker'] = self.worker
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timesheet_worker'] = self.worker
        context['report'] = Timer.objects.get_monthly_worker_report(context['report_period'], self.worker)
        return context

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class TimerDeleteView(DeleteView):
    model = Timer

    def get_success_url(self):
        return reverse_lazy('timetracking_worker', kwargs={'worker_id': self.object.worker.id})


class TimerDeleteSelectedDayView(ListView):
    template_name = 'timetracking/timers_confirm_delete.html'

    def get_queryset(self):
        selected_day = datetime.datetime.strptime(self.kwargs['selected_day'], '%Y-%m-%d').date()
        timers = Timer.objects.filter(started__date=selected_day).filter(worker_id=self.kwargs['worker_id'])
        return timers

    def get_context_data(self, **kwargs):
        timers = [timer for timer in self.get_queryset()]
        current_timer = timers[0]
        for timer in timers:
            if timer.started < current_timer.started:
                current_timer.started = timer.started
            if timer.stopped > current_timer.stopped:
                current_timer.stopped = timer.stopped
        timerange = "{:%Y-%m-%d} {:%H:%M} -> {:%H:%M}".format(
            timezone.localtime(current_timer.started).date(),
            timezone.localtime(current_timer.started),
            timezone.localtime(current_timer.stopped)
        )
        return super().get_context_data(timerange=timerange)

    def post(self, request, *args, **kwargs):
        timers = self.get_queryset()
        timers.delete()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('timetracking_worker', kwargs={'worker_id': self.kwargs['worker_id']})
