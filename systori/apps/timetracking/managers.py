from datetime import datetime, timedelta, date
from collections import OrderedDict

from django.db.models.query import QuerySet
from django.db.models import F, Sum, Min, Max, Func
from django.utils import timezone
from django.contrib.auth import get_user_model


class TimerQuerySet(QuerySet):

    def get_duration(self):
        return self.aggregate(total_duration=Sum('duration'))['total_duration'] or 0

    def filter_running(self):
        return self.filter(end__isnull=True)

    def filter_today(self):
        return self.filter(start__gte=timezone.now().date())

    def filter_period(self, year=None, month=None):
        date_filter = {}
        assert not (month and not year), 'Cannot generate report by month without a year specified'
        if year:
            date_filter['start__year'] = year
            if month:
                date_filter['start__month'] = month
        else:
            now = timezone.now()
            date_filter['start__year'] = now.year
            date_filter['start__month'] = now.month
        return self.filter(**date_filter)

    def group_for_report(self, order_by='-day_start'):
        current_timezone = timezone.get_current_timezone()
        current_offset = current_timezone.utcoffset(datetime.now()).seconds
        queryset = self.extra(
            select={
                'date': 'date(start + interval \'{} seconds\')'.format(current_offset)
            }
        ).values('kind', 'date', 'user_id').order_by().annotate(
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

    def generate_user_report_data(self, period):
        from calendar import monthrange
        from .utils import format_seconds

        period = period or timezone.now()
        queryset = self.filter_period(period.year, period.month).group_for_report(order_by='day_start')
        report = OrderedDict()
        for row in queryset:
            report_row = report.setdefault(row['date'], [])
            print(row)
            if row['kind'] == self.model.WORK:
                duration_calculator = self.model.duration_formulas[self.model.WORK]
                next_day = timezone.make_aware(
                    datetime.combine(row['date'] + timedelta(days=1), datetime.min.time()),
                    timezone.get_current_timezone()
                )
                total_duration = row['total_duration']
                # We have a running timer (possibly with existing stopped timers)
                if not row['day_end'] or row['latest_start'] > row['day_end']:
                    total_duration += duration_calculator(row['latest_start'], next_day)

                if row['total_duration'] >= self.model.DAILY_BREAK:
                    total = total_duration - self.model.DAILY_BREAK
                else:
                    total = total_duration

                overtime = total - self.model.WORK_HOURS if total > self.model.WORK_HOURS else 0
                report_row.append({
                    'kind': 'work',
                    'total_duration': total_duration,
                    'total': total,
                    'overtime': overtime,
                    'day_start': row['day_start'],
                    'day_end': row['day_end']
                })
            elif row['kind'] == self.model.HOLIDAY:
                report_row.append({
                    'kind': 'holiday',
                    'day_start': row['day_start'],
                    'total_duration': row['total_duration']
                })
            elif row['kind'] == self.model.ILLNESS:
                report_row.append({
                    'kind': 'illness',
                    'day_start': row['day_start'],
                    'total_duration': row['total_duration']
                })
        return report

    def generate_report_data(self):
        report_data = self.group_for_report()
        now = timezone.now()

        for day in report_data:
            # real_day_end = timezone.make_aware(
            #     datetime.combine(day['date'], datetime.max.time()),
            #     timezone.get_current_timezone()
            # )
            duration_calculator = self.model.duration_formulas[day['kind']]

            # We have a running timer (possibly with existing stopped timers)
            if not day['day_end'] or day['latest_start'] > day['day_end']:
                day['total_duration'] += duration_calculator(day['latest_start'], now)

            if day['total_duration'] >= self.model.DAILY_BREAK:
                total = day['total_duration'] - self.model.DAILY_BREAK
            else:
                total = day['total_duration']
            overtime = total - self.model.WORK_HOURS if total > self.model.WORK_HOURS else 0
            day.update({
                'total': total,
                'overtime': overtime
            })
            yield day
