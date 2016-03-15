from django.db.models.query import QuerySet
from django.db.models import F, Sum


class TimerQuerySet(QuerySet):

    def get_running(self):
        return self.filter(end__isnull=True)

    def report(self):
        self.extra(select={'date': 'date(start)'}).annotate(
            total_duration=F('duration') - self.model.DAILY_BREAK
        ).values('date', 'total_duration').annotate(Sum('total_duration'))
