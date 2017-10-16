from datetime import date, time, datetime, timedelta
from collections import OrderedDict

from django.db.models.query import QuerySet
from django.db.models import Q
from django.db.transaction import atomic
from django.utils.timezone import localtime, localdate, now, utc, make_aware
from systori.lib.utils import GenOrderedDict, local_day_in_utc, local_month_range_in_utc
from ..company.models import Company, Worker
from .utils import get_timespans_split_by_breaks, get_dates_in_range


class TimerQuerySet(QuerySet):

    def current(self):
        """ Running or stopped timers that apply to current time (now). """
        utc_now = now()
        return self.filter(Q(started__lte=utc_now), Q(stopped__gte=utc_now) | Q(stopped__isnull=True))

    def running(self, **kwargs):
        """ Running timers. """
        return self.filter(stopped__isnull=True, **kwargs)

    def day(self, day: date=None, **kwargs):
        """ Timers that were started within the beginning and end of the day in local time. """
        return self.filter(started__range=local_day_in_utc(day), **kwargs)

    def month(self, year, month, **kwargs):
        """ All timers for current month (localized). """
        return self.filter(started__range=local_month_range_in_utc(year, month), **kwargs)

    def get_running_timer(self, worker, **kwargs):
        return self.running(worker=worker, **kwargs).first()

    def get_workers(self):
        return Worker.objects \
            .filter(pk__in=self.values_list('worker_id')) \
            .order_by('user__last_name')

    def get_report(self, grouping='date'):
        assert grouping in ('date', 'worker')

        report = GenOrderedDict(
            lambda: GenOrderedDict(
                lambda: {
                    'timers': [],
                    'total': 0
                }
            )
        )

        for timer in self:
            dt = localdate(timer.started)
            if grouping == 'date':
                worker_report = report.gen(dt).gen(timer.worker)
            else:
                worker_report = report.gen(timer.worker).gen(dt)
            worker_report['timers'].append(timer)
            if timer.kind != timer.UNPAID_LEAVE:
                worker_report['total'] += timer.running_duration

        for parent_report in report.values():
            for worker_report in parent_report.values():
                previous = None
                with_breaks = []
                for timer in worker_report['timers']:
                    if previous:
                        with_breaks.append(self.model(
                            worker=timer.worker,
                            started=previous.stopped,
                            stopped=timer.started,
                            kind=self.model.BREAK
                        ))
                    with_breaks.append(timer)
                    previous = timer
                worker_report['timers'] = with_breaks

        return report

    def get_daily_workers_report(self, day: date):
        assert isinstance(day, date)
        report = OrderedDict(
            (worker, {'timers': [], 'total': 0})
            for worker in Company.active().tracked_workers()
        )
        report.update(
            self.day(day)
            .select_related('worker__user')
            .order_by('started')
            .get_report('date')
            .get(day, {})
        )
        return report

    def get_monthly_worker_report(self, month: date, worker):
        assert isinstance(month, date)
        return (
            self.month(month.year, month.month, worker=worker)
            .order_by('started')
            .get_report('worker')
            .get(worker, {})
        )

    def get_vacation_schedule(self, year: date):
        assert isinstance(year, date)
        schedule = {}
        workers = [worker for worker in Company.active().tracked_workers()]
        for worker in workers:
            schedule[worker] = {}
            for month in range(1,13):
                schedule[worker][month] = 0
            schedule[worker]['total'] = 0
            schedule[worker]['available'] = 0
        for timer in self.filter(worker__in=workers, started__year=year.year, kind='vacation').order_by('started'):
            schedule[timer.worker][timer.started.month] += timer.duration
            schedule[timer.worker]['total'] += timer.duration
        for worker in schedule:
            schedule[worker]['available'] = worker.contract.vacation * 12 - schedule[worker]['total']
        return schedule

    def create_batch(self, worker, dates: datetime, start: time, stop: time,
                     commit=True, morning_break=True, lunch_break=True, **kwargs):

        begin, end = dates

        # days contains local dates on which timers will be created
        days = []
        if not end or begin == end:  # explicit single day, skip weekend & .exists() checks
            days.append(begin)
        else:
            for day in get_dates_in_range(begin, end):
                if not self.day(day, worker=worker).exists():
                    days.append(day)

        breaks = []
        if morning_break:
            breaks.append(worker.contract.morning_break)
        if lunch_break:
            breaks.append(worker.contract.lunch_break)

        time_spans = list(get_timespans_split_by_breaks(start, stop, breaks))

        timers = []
        for day in days:
            for start_time, end_time in time_spans:
                timer = self.model(worker=worker, **kwargs)
                timer.started = make_aware(datetime.combine(day, start_time))
                timer.stopped = make_aware(datetime.combine(day, end_time))
                timers.append(timer)
                if commit:
                    timer.save()

        return timers

    @atomic
    def stop_abandoned(self):
        for worker in Company.active().tracked_workers():
            timer = self.get_running_timer(worker, kind=self.model.WORK)
            if timer:
                work_end = worker.contract.work_end
                penalty = timedelta(minutes=worker.contract.abandoned_timer_penalty)  # negative duration
                cutoff = localtime().replace(hour=work_end.hour, minute=work_end.minute).astimezone(utc)
                if timer.started >= cutoff:
                    # timer was started after work day ended...
                    # set it to 5 minutes at least so it doesn't get auto deleted...
                    timer.stop(stopped=timer.started + timedelta(minutes=5), is_auto_stopped=True)
                else:
                    duration = cutoff - timer.started  # start of timer to end of work day
                    duration_w_penalty = duration + penalty  # start of timer to work day + penalty
                    if duration_w_penalty > timedelta(minutes=1):  # timer still valid after pently?
                        timer.stop(stopped=timer.started + duration_w_penalty, is_auto_stopped=True)
                    elif duration > timedelta(minutes=1):  # timer still valid after cutoff?
                        timer.stop(stopped=timer.started + duration, is_auto_stopped=True)
                    else:  # just stop timer with 1 minute duration
                        timer.stop(stopped=timer.started + timedelta(minutes=1), is_auto_stopped=True)

    def start_or_stop_work_breaks(self):
        utc_now = now().replace(second=0, microsecond=0)
        local = localtime(utc_now)
        local_time = local.time()
        for worker in Company.active().tracked_workers():
            if local_time in [b.start for b in worker.contract.breaks]:
                # Stop running timers to begin break
                timer = self.get_running_timer(worker, kind=self.model.WORK)
                if timer:
                    timer.stop(stopped=utc_now, is_auto_stopped=True)
            elif local_time in [b.end for b in worker.contract.breaks]:
                # Start timers to end break
                had_auto_stopped = self.day(
                    local.date(), worker=worker, kind=self.model.WORK, is_auto_stopped=True
                ).exists()
                running = self.get_running_timer(worker)
                if had_auto_stopped and not running:
                    self.model.start(worker, started=utc_now, is_auto_started=True)
