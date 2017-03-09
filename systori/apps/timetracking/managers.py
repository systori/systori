from datetime import date, datetime, timedelta

from django.db.models.query import QuerySet
from django.db.models import Q, Sum
from django.db.transaction import atomic
from django.utils import timezone
from .utils import get_timespans_split_by_breaks, get_dates_in_range
from systori.lib import date_utils
from systori.lib.utils import GenOrderedDict
from ..company.models import Worker

ABANDONED_CUTOFF = (16, 00)


class TimerQuerySet(QuerySet):

    def get_duration(self):
        return self.aggregate(total_duration=Sum('duration'))['total_duration'] or 0

    def filter_running(self):
        return self.filter(stopped__isnull=True)

    @atomic
    def stop_abandoned(self):
        """
        Stop timers still running at the end of the day
        """
        cutoff_params = dict(hour=ABANDONED_CUTOFF[0], minute=ABANDONED_CUTOFF[1], second=0, microsecond=0)
        for timer in self.filter_running():
            if (timer.started.hour, timer.started.minute) >= ABANDONED_CUTOFF:
                timer.stop(stopped=timer.started + timedelta(minutes=5))
            else:
                timer.stop(stopped=timer.started.replace(**cutoff_params))

    def stop_for_break(self, stopped=None):
        """
        Stop currently running timers automatically.
        Doesn't validate if it's time for break now or not.
        """
        stopped = stopped or timezone.now()
        counter = 0
        for timer in self.filter_running().filter(kind=self.model.WORK):
            timer.stop(stopped=stopped, is_auto_stopped=True)
            counter += 1
        return counter

    def launch_after_break(self, started=None):
        """
        Launch timers for workers that had timers automatically stopped.
        """
        started = started or timezone.now()
        seen_workers = set()
        auto_stopped_timers = self.filter_today().filter(
            kind=self.model.WORK, is_auto_stopped=True).select_related('worker')
        running_workers = self.filter_running().values_list('worker')
        for timer in auto_stopped_timers.exclude(worker__in=running_workers):
            if not timer.worker in seen_workers:
                self.model.start(timer.worker, started=started, is_auto_started=True)
                seen_workers.add(timer.worker)
        return len(seen_workers)

    def filter_now(self, now: datetime=None):
        now = now or timezone.now()
        return self.filter(Q(stopped__gte=now) | Q(stopped__isnull=True), started__lte=now)

    def filter_today(self):
        return self.filter(started__date=timezone.now().date())

    def filter_month(self, year=None, month=None):
        if year is not None:
            assert month is not None
        else:
            now = timezone.now()
            year, month = now.year, now.month
        return self.filter(started__date__range=date_utils.month_range(year, month))

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
            date = timer.started.date()
            if grouping == 'date':
                worker_report = report.gen(date).gen(timer.worker)
            else:
                worker_report = report.gen(timer.worker).gen(date)
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

    def get_daily_workers_report(self, day: date, workers):
        assert isinstance(day, date)
        return self \
            .filter(worker__in=workers) \
            .filter(started__date=day) \
            .select_related('worker__user') \
            .order_by('worker__user__last_name', 'started') \
            .get_report('date') \
            .get(day, {})

    def create_batch(self, worker, started: datetime, stopped: datetime, commit=True,
                     morning_break=True, lunch_break=True, **kwargs):

        # Enforce timezone
        tz = worker.company.timezone
        assert all(dt.tzinfo.zone == tz.zone for dt in (started, stopped))

        days = []
        if (stopped - started).days == 0:  # explicit single day, skip weekend & .exists() checks
            days.append(started)
        else:
            for day in get_dates_in_range(started.date(), stopped.date()):
                if not self.filter(worker=worker, started__date=day).exists():
                    days.append(day)

        breaks = []
        if morning_break:
            breaks.append(worker.company.breaks[0])
        if lunch_break:
            breaks.append(worker.company.breaks[1])

        time_spans = list(get_timespans_split_by_breaks(started.time(), stopped.time(), breaks))

        timers = []
        for day in days:
            for start_time, end_time in time_spans:
                timer = self.model(worker=worker, **kwargs)
                timer.started = tz.localize(datetime.combine(day, start_time))
                timer.stopped = tz.localize(datetime.combine(day, end_time))
                timers.append(timer)
                if commit:
                    timer.save()

        return timers

    def get_workers(self):
        return Worker.objects \
            .filter(pk__in=self.values_list('worker')) \
            .order_by('user__last_name')
