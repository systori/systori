from django.db.models.query import QuerySet
from django.db.models import F, Sum, Min, Max
from django.utils import timezone


class TimerQuerySet(QuerySet):

    def get_running(self):
        return self.filter(end__isnull=True)

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

    def generate_report_data(self, year=None, month=None):
        report_data = self.filter_period(year, month).extra(
            select={'date': 'date(start)'}
        ).values('date').annotate(
            total_duration=Sum('duration'),
            start=Min('start'),
            end=Max('end')
        ).order_by('-start')

        for day in report_data:
            total = day['total_duration'] - self.model.DAILY_BREAK
            overtime = total - self.model.WORK_HOURS if total > self.model.WORK_HOURS else 0
            day.update({
                'total': total,
                'overtime': overtime
            })
            yield day
