from collections import OrderedDict
from math import floor, ceil
from calendar import monthrange
from datetime import date
from django.utils.timezone import localtime, utc


def local_day_in_utc(day: date=None):
    """ Returns the start/end date times for local day in UTC. """
    local = localtime()
    if day is not None:
        local = local.replace(day.year, day.month, day.day)
    return (
        local.replace(hour=0, minute=0, second=0).astimezone(utc),
        local.replace(hour=23, minute=59, second=59).astimezone(utc)
    )


def local_month_range_in_utc(year: int, month: int):
    """ Returns the start/end date times in UTC for the first
        and last local day of a particular month.
        Useful in query filter, ex:
          .filter(started__range=local_month_range_in_utc(2016, 8))
        Produces:
          WHERE "started" BETWEEN 2016-08-01 AND 2016-08-31
    """
    local = localtime()
    return (
        local.replace(year, month, 1, 0, 0, 0).astimezone(utc),
        local.replace(year, month, monthrange(year, month)[1], 23, 59, 59).astimezone(utc)
    )


def nice_percent(progress, total):
    percent = progress / total * 100 if total else 0
    if percent < 100:
        return ceil(percent)
    elif percent > 100:
        return floor(percent)
    else:
        return 100


class GenOrderedDict(OrderedDict):
    """

        OrderedDict with `.gen()` method which
        works similar to `.setdefault()`.

        Example usage:

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
            day_report = report.gen(date)
            worker_report = day_report.gen(timer.worker)
            worker_report['timers'].append(timer)
            if timer.kind != timer.UNPAID_LEAVE:
                worker_report['total'] += timer.running_duration
    """
    def __init__(self, generator):
        super().__init__()
        self.generator = generator

    def gen(self, key):
        return self.setdefault(key, self.generator())
