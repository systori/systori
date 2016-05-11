from django.db.models.query import QuerySet
from django.db.models import F, Sum, Min, Max
from django.utils import timezone
from django.contrib.auth import get_user_model


class TimerQuerySet(QuerySet):

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

    def group_for_report(self):
        return self.extra(
            select={'date': 'date(start)'}
        ).values('kind', 'date', 'user_id').order_by().annotate(
            total_duration=Sum('duration'),
            day_start=Min('start'),
            latest_start=Max('start'),
            end=Max('end')
        ).order_by('-day_start')

    def generate_report_data(self, now=None):
        report_data = self.group_for_report()

        if not now:
            now = timezone.now()
        for day in report_data:
            duration_calculator = self.model.duration_formulas[day['kind']]

            # if not day['end'] and day['day_start']:
            #     day['total_duration'] += duration_calculator(day['day_start'], timezone.now())
            if not day['end'] or day['latest_start'] > day['end']:
                # We have a running timer (possibly with existing stopped timers)
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
