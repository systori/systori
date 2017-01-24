from datetime import time, timedelta, date, datetime
from collections import UserDict, namedtuple
from typing import Iterator, Tuple

from django.utils import timezone


WORK_DAY = timedelta(hours=8).total_seconds()
HOLIDAYS_PER_MONTH = WORK_DAY * 2.5


class AccumulatorDict(UserDict):

    def __setitem__(self, key, value):
        self.data.setdefault(key, []).append(value)


def regroup(items, getter):
    result = {}
    for item in items:
        result[getter(item)] = item
    return result


def seconds_to_time(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    if minutes > 0:
        if seconds >= 30:
            minutes += 1
            seconds = 0
        else:
            seconds = 0
    hours, minutes = divmod(minutes, 60)
    try:
        return time(hours, minutes, seconds)
    except ValueError:
        return time(0, 0, 0)


def format_seconds(seconds, strftime_format='%-H:%M'):
    negative = False
    if seconds < 0:
        negative = True
        seconds = abs(seconds)
    return ('-' if negative else '') + seconds_to_time(seconds).strftime(strftime_format)


def format_days(seconds):
    return '{:.1f}'.format(seconds / WORK_DAY)


def to_current_timezone(date_time):
    return date_time.astimezone(timezone.get_current_timezone())


def round_to_nearest_multiple(seconds, multiplier=36):
    remainder = seconds % multiplier
    if remainder >= (multiplier/2):
        return seconds + (multiplier-remainder)
    else:
        return seconds - remainder

### Reports


def get_worker_dashboard_report(worker):
    from .models import Timer
    now = timezone.now()
    timers = Timer.objects.filter_month(now.year, now.month).filter(
        worker=worker, kind=Timer.WORK).order_by('start')
    return timers


def get_worker_monthly_report(worker, period):
    from .models import Timer
    period = period or timezone.now()

    holidays_used = get_holidays_duration(worker, period.year, period.month)
    report = Timer.objects.filter(worker=worker).generate_monthly_worker_report(period)
    overtime = sum(day['work']['overtime'] for day in report.values())
    return {
        'holidays_used': format_days(holidays_used),
        'holidays_available': format_days(HOLIDAYS_PER_MONTH - holidays_used),
        'rows': report,
        'overtime': overtime,
    }


def get_holidays_duration(worker, year, month):
    from .models import Timer
    return Timer.objects.filter(worker=worker, kind=Timer.HOLIDAY).filter_month(year, month).get_duration()


def get_overtime_duration(worker, year, month):
    from .models import Timer
    return Timer.objects.filter(worker=worker, kind=Timer.HOLIDAY).filter_month(year, month).get_duration()


def get_daily_workers_report(workers, date=None):
    from .models import Timer

    return Timer.objects.generate_daily_workers_report(date=date, workers=workers)
    # report_by_user = regroup(report, itemgetter('user_id'))
    # for user in users:
    #     yield {'user': user, 'report': report_by_user.get(user.pk)}


def get_running_timer_duration(worker):
    from .models import Timer
    timer = Timer.objects.filter_running().filter(worker=worker).first()
    duration = timer.get_duration_seconds() if timer else 0
    return format_seconds(duration, '%H:%M:%S')


def get_workers_statuses(workers):
    from .models import Timer
    timers = Timer.objects.filter(worker__in=workers).filter_now()
    worker_timers = AccumulatorDict()
    for timer in timers:
        worker_timers[timer.worker_id] = timer
    return worker_timers


def get_dates_in_range(start: date, end: date, include_weekends=False) -> Iterator[date]:
    current = start
    while end >= current:
        if include_weekends or current.weekday() not in (5, 6):
            yield current
        current += timedelta(days=1)


BreakSpan = namedtuple('BreakSpan', ('start', 'end'))


def get_timespans_split_by_breaks(start_time: time, end_time: time, breaks) -> Iterator[Tuple[time, time]]:
    """ This function is timezone unaware. Time range and breaks must
        be in the same local timezone. Breaks must be in chronological order.
    """
    next_start = start_time
    # Apply Breaks
    for break_span in breaks:
        if next_start <= break_span.start:
            end = min(break_span.start, end_time)
            if next_start < end:
                yield next_start, end
            next_start = break_span.end
    # Apply Remainder
    if next_start < end_time:
        yield next_start, end_time


def perform_autopilot_duties(breaks, tz):
    """
    Issue timers stop or launch commands at certain times of day
    """
    from .models import Timer

    now = datetime.now(tz).replace(second=0, microsecond=0)
    time_now = now.time()
    if time_now in [b.start for b in breaks]:
        Timer.objects.stop_for_break(now)
    elif time_now in [b.end for b in breaks]:
        Timer.objects.launch_after_break(now)
