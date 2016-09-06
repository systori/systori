from datetime import datetime, timedelta, time
from collections import OrderedDict

from pytz import timezone as pytz_timezone
from django.db.models.query import QuerySet
from django.db.models import F, Q, Sum, Min, Max, Func
from django.db.transaction import atomic
from django.utils import timezone
from django.contrib.auth import get_user_model
from .utils import get_timespans_split_by_breaks, get_dates_in_range
from systori.lib import date_utils


ABANDONED_CUTOFF = (16, 00)


class TimerQuerySet(QuerySet):

    def get_duration(self):
        return self.aggregate(total_duration=Sum('duration'))['total_duration'] or 0

    def filter_running(self):
        return self.filter(end__isnull=True).exclude(kind=self.model.CORRECTION)

    @atomic
    def stop_abandoned(self):
        """
        Stop timers still running at the end of the day
        """
        cutoff_params = dict(hour=ABANDONED_CUTOFF[0], minute=ABANDONED_CUTOFF[1], second=0, microsecond=0)
        for timer in self.filter_running():
            if (timer.start.hour, timer.start.minute) >= ABANDONED_CUTOFF:
                timer.stop(end=timer.start + timedelta(minutes=5))
            else:
                timer.stop(end=timer.start.replace(**cutoff_params))

    def stop_for_break(self, end=None):
        """
        Stop currently running timers automatically.
        Doesn't validate if it's time for break now or not.
        """
        end = end or timezone.now()
        counter = 0
        for timer in self.filter_running().filter(kind=self.model.WORK):
            timer.stop(end=end, is_auto_stopped=True)
            counter += 1
        return counter

    def launch_after_break(self, start=None):
        """
        Launch timers for users that had timers automatically stopped.
        """
        start = start or timezone.now()
        seen_users = set()
        auto_stopped_timers = self.filter_today().filter(
            kind=self.model.WORK, is_auto_stopped=True).select_related('user')
        running_users = self.filter_running().values_list('user')
        for timer in auto_stopped_timers.exclude(user__in=running_users):
            if not timer.user in seen_users:
                self.model.launch(timer.user, start=start, is_auto_started=True)
                seen_users.add(timer.user)
        return len(seen_users)

    def filter_today(self):
        return self.filter_date(date=None)

    def filter_date(self, date=None):
        date = date or timezone.now().date()
        start = datetime.combine(date, datetime.min.time())
        end = start + timedelta(days=1)
        return self.filter(Q(end__lt=end) | Q(end__isnull=True), start__gte=start)

    def filter_now(self, now=None):
        now = now or timezone.now()
        return self.filter(Q(end__gte=now) | Q(end__isnull=True), start__lte=now)

    def filter_month(self, year=None, month=None):
        if year is not None:
            assert month is not None
        else:
            now = timezone.now()
            year, month = now.year, now.month
        return self.filter(date__range=date_utils.month_range(year, month))

    def group_for_report(self, order_by='-day_start', separate_by_kind=False):
        # TODO: Refactor/remove in favor of using non-aggregated Timer queryset (a la generate_daily_users_report)
        current_timezone = timezone.get_current_timezone()
        grouping_values = ['date', 'user_id', 'comment']
        if separate_by_kind:
            grouping_values.insert(0, 'kind')

        queryset = self.values(*grouping_values).order_by().annotate(
            total_duration=Sum('duration'),
            day_start=Min('start'),
            latest_start=Max('start'),
            day_end=Max('end')
        ).order_by(order_by)
        for day in queryset:
            for field in ('day_start', 'day_end', 'latest_start'):
                if not day[field]:
                    continue
                day[field] = day[field].astimezone(current_timezone)
            yield day

    def generate_monthly_user_report(self, period=None):
        from .utils import format_seconds

        naive_now = datetime.now()
        now = timezone.now()
        period = period or timezone.now()
        queryset = self.filter_month(period.year, period.month)

        report = OrderedDict()
        for timer in queryset:
            report.setdefault(timer.date, OrderedDict({
                'work': {
                    'start': None,
                    'end': None,
                    'duration': 0,
                    'overtime': 0,
                    'total': 0,
                    'locations': []
                },
                'holiday': {
                    'start': None,
                    'end': None,
                    'duration': 0,
                },
                'illness': {
                    'start': None,
                    'end': None,
                    'duration': 0,
                },
                'correction': {
                    'start': None,
                    'end': None,
                    'duration': 0,
                },
                'education': {
                    'start': None,
                    'end': None,
                    'duration': 0,
                }
            }))
            report_row = report[timer.start.date()][timer.kind]
            if not report_row['start'] or report_row['start'] > timer.start:
                report_row['start'] = timer.start
            if report_row['end'] and timer.end and timer.end > report_row['end']:
                report_row['end'] = timer.end
            else:
                if timer.end:
                    report_row['end'] = timer.end
                else:
                    report_row['end'] = now
            report_row['duration'] += timer.get_duration_seconds(now)
            if timer.kind == self.model.WORK:
                report_row['total'] += timer.get_duration_seconds(now)
                report_row['overtime'] = report_row['duration'] - self.model.WORK_HOURS
                report_row['total'] += report_row['overtime']
                report_row['locations'].append(
                    ((timer.start_latitude, timer.start_longitude), (timer.end_latitude, timer.end_longitude))
                )
        return report

    def generate_daily_users_report(self, date, users):
        from .utils import format_seconds
        date = date or timezone.now().date()
        day_start = timezone.make_aware(
            datetime.combine(date, datetime.min.time()),
            timezone.get_current_timezone()
        )
        queryset = self.filter(user__in=users).filter_date(date).select_related('user')
        reports = OrderedDict((user, {
            'day_start': None,
            'day_end': None,
            'total_duration': 0,
            'total': 0,
            'overtime': 0
        }) for user in users)
        for timer in queryset:
            user_report = reports[timer.user]
            if not user_report['day_start'] or user_report['day_start'] > timer.start:
                user_report['day_start'] = timer.start

            if not user_report['day_end'] or timer.end and timer.end > user_report['day_end']:
                user_report['day_end'] = timer.end
            user_report['total_duration'] += timer.get_duration_seconds()

        for _, report_data in reports.items():
            if report_data['total_duration'] >= self.model.DAILY_BREAK:
                report_data['total'] = report_data['total_duration'] - self.model.DAILY_BREAK
            else:
                report_data['total'] = report_data['total_duration']
            report_data['overtime'] = report_data['total'] - self.model.WORK_HOURS
        return reports

    def create_batch(self, user, start: datetime, end: datetime, commit=True, include_weekends=False, **kwargs):
        tz = user.company.timezone

        # Requested start/end times must be of the same timezone as the company breaks.
        assert all(dt.tzinfo.zone == tz.zone for dt in (start, end))
        time_spans = list(get_timespans_split_by_breaks(start.time(), end.time(), user.company.breaks))

        timers = []
        for day in get_dates_in_range(start.date(), end.date(), include_weekends):
            for start_time, end_time in time_spans:
                timer = self.model(user=user, **kwargs)
                timer.date = day
                timer.start = tz.localize(datetime.combine(day, start_time))
                timer.end = tz.localize(datetime.combine(day, end_time))
                timers.append(timer)
                if commit: timer.save()

        return timers
