import datetime

from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import BaseCreateView, DeleteView
from django.views.generic.list import ListView
from django.utils import timezone
from django.utils.functional import cached_property

from . import utils
from . import forms
from .models import Timer


class PeriodFilterMixin(TemplateView):
    period_form_class = None

    def get_context_data(self, **kwargs):
        report_period = timezone.now().date()
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
        context['report'] = utils.get_daily_workers_report(
            utils.get_timetracking_workers(self.request.company).order_by('user__last_name'),
            context['report_period'],
        )
        return context

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class WorkerReportView(BaseCreateView, PeriodFilterMixin):
    template_name = 'timetracking/user_report.html'
    form_class = forms.WorkerManualTimerForm
    period_form_class = forms.MonthPickerForm

    @cached_property
    def worker(self):
        return get_object_or_404(
            utils.get_timetracking_workers(self.request.company), pk=self.kwargs['worker_id'])

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
        context['report'] = utils.get_worker_monthly_report(
            context['timesheet_worker'],
            context['report_period']
        )
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
