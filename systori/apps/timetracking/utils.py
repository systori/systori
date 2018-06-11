from datetime import time, timedelta, date, datetime
from collections import namedtuple
from typing import Iterator, Tuple

from django.utils import timezone

from systori.lib.templatetags.customformatting import hours


def calculate_duration_minutes(started, stopped=None):
    if stopped is None:
        stopped = timezone.now()
    started = started.replace(second=0, microsecond=0)
    stopped = stopped.replace(second=0, microsecond=0)
    seconds = (stopped - started).total_seconds()
    return int(seconds // 60)


def calculate_duration_seconds(started, stopped=None):
    if stopped is None:
        stopped = timezone.now()
    started = started.replace(microsecond=0)
    stopped = stopped.replace(microsecond=0)
    seconds = (stopped - started).total_seconds()
    return int(seconds)


def to_current_timezone(date_time):
    return date_time.astimezone(timezone.get_current_timezone())


def get_workers_statuses():
    from .models import Timer

    return dict((timer.worker_id, timer) for timer in Timer.objects.current())


def get_dates_in_range(
    start: date, end: date, include_weekends=False
) -> Iterator[date]:
    current = start
    while end >= current:
        if include_weekends or current.weekday() not in (5, 6):
            yield current
        current += timedelta(days=1)


BreakSpan = namedtuple("BreakSpan", ("start", "end"))


def get_timespans_split_by_breaks(
    start_time: time, end_time: time, breaks
) -> Iterator[Tuple[time, time]]:
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
