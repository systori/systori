from datetime import datetime, timedelta
from collections import OrderedDict

from pytz import timezone as pytz_timezone
from django.db.models.query import QuerySet
from django.db.models import F, Q, Sum, Min, Max, Func
from django.db.transaction import atomic
from django.utils import timezone
from django.contrib.auth import get_user_model


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

    def stop_for_break(self):
        """
        Stop currently running timers automatically.
        Doesn't validate if it's time for break now or not.
        """
        end = timezone.now()
        counter = 0
        for timer in self.filter_running().filter(kind=self.model.WORK):
            timer.stop(end=end, is_auto_stopped=True)
            counter += 1
        return counter

    def launch_after_break(self):
        """
        Launch timers for users that had timers automatically stopped.
        """
        start = timezone.now()
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
        date_filter = {}
        assert not (month and not year), 'Cannot generate report by month without a year specified'
        if year:
            date_filter['date__year'] = year
            if month:
                date_filter['date__month'] = month
        else:
            now = timezone.now()
            date_filter['date__year'] = now.year
            date_filter['date__month'] = now.month
        return self.filter(**date_filter)

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
            if not report_row['end'] or timer.end > report_row['end']:
                report_row['end'] = timer.end
            report_row['duration'] += timer.get_duration_seconds(now)
            if timer.kind == self.model.WORK:
                report_row['total'] += timer.get_duration_seconds(now)
                timer_start_time = (timer.start.hour, timer.start.minute)
                timer_end = timer.end or now
                timer_end_time = (timer_end.hour, timer_end.minute)
                # TODO: This is a hack for dealing with the timezone insanity, should fix it later
                offset = pytz_timezone('CET').utcoffset(naive_now).total_seconds() / 60 / 60
                first_break_start = (9 - offset, 00)
                first_break_end = (9 - offset, 30)
                second_break_start = (12 - offset, 30)
                second_break_end = (13 - offset, 00)
                if first_break_start >= timer_start_time and timer_end_time >= first_break_end:
                    report_row['total'] -= self.model.DAILY_BREAK * 0.5
                if second_break_start >= timer_start_time and timer_end_time >= second_break_end:
                    report_row['total'] -= self.model.DAILY_BREAK * 0.5
                if report_row['duration'] > self.model.WORK_HOURS:
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

    def create_batch(self, days, user, start, **kwargs):
        kwargs.pop('end', None)
        assert kwargs.get('kind') in self.model.FULL_DAY_KINDS
        day_start_hour, day_start_minute = self.model.WORK_DAY_START
        start = start.replace(hour=day_start_hour, minute=day_start_minute, second=0, microsecond=0)
        duration = self.model.WORK_HOURS
        timers = [
            self.model(user=user, start=start + timedelta(days=d), duration=duration, **kwargs)
            for d in range(days)
        ]
        for timer in timers:
            timer.save()
        return timers
