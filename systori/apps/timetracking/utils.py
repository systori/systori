from datetime import time, timedelta, datetime
from collections import UserDict

from django.utils import timezone


WORK_DAY = timedelta(hours=8).total_seconds()
HOLIDAYS_PER_MONTH = WORK_DAY * 2.5
BREAKS = [
    (time(9, 00), time(9, 30)),
    (time(12, 30), time(13, 00)),
]


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


def get_user_dashboard_report(user):
    from .models import Timer
    now = timezone.now()
    timers = Timer.objects.filter_month(now.year, now.month).filter(
        user=user, kind=Timer.WORK).order_by('start')
    return timers


def get_user_monthly_report(user, period):
    from .models import Timer
    period = period or timezone.now()

    holidays_used = get_holidays_duration(user, period.year, period.month)
    report = Timer.objects.filter(user=user).generate_monthly_user_report(period)
    overtime = sum(day['work']['overtime'] for day in report.values())
    return {
        'holidays_used': format_days(holidays_used),
        'holidays_available': format_days(HOLIDAYS_PER_MONTH - holidays_used),
        'rows': report,
        'overtime': overtime,
    }


def get_holidays_duration(user, year, month):
    from .models import Timer
    return Timer.objects.filter(user=user, kind=Timer.HOLIDAY).filter_month(year, month).get_duration()


def get_overtime_duration(user, year, month):
    from .models import Timer
    return Timer.objects.filter(user=user, kind=Timer.HOLIDAY).filter_month(year, month).get_duration()


def get_daily_users_report(users, date=None):
    from .models import Timer

    return Timer.objects.generate_daily_users_report(date=date, users=users)
    # report_by_user = regroup(report, itemgetter('user_id'))
    # for user in users:
    #     yield {'user': user, 'report': report_by_user.get(user.pk)}


def get_running_timer_duration(user):
    from .models import Timer
    timer = Timer.objects.filter_running().filter(user=user).first()
    duration = timer.get_duration_seconds() if timer else 0
    return format_seconds(duration, '%H:%M:%S')


def get_users_statuses(users):
    from .models import Timer
    timers = Timer.objects.filter(user__in=users).filter_now()
    user_timers = AccumulatorDict()
    for timer in timers:
        user_timers[timer.user.pk] = timer
    return user_timers


def get_dates_in_range(start_date, end_date, delta, include_weekends=False):
    current_date = start_date
    while end_date > current_date:
        if include_weekends or current_date.weekday() not in (5, 6):
            yield current_date
        current_date += delta


def get_timespans_split_by_breaks(day_start, day_end, datetime_list):
    for day in datetime_list:
        next_start = day_start
        # Apply Breaks
        for span in BREAKS:
            if next_start <= span[0]:
                start = day.replace(hour=next_start.hour, minute=next_start.minute)
                end_time = min(span[0], day_end)
                end = day.replace(hour=end_time.hour, minute=end_time.minute)
                if start < end:
                    yield start, end
                next_start = span[1]
        # Apply Remainder
        if next_start < day_end:
            start = day.replace(hour=next_start.hour, minute=next_start.minute)
            end = day.replace(hour=day_end.hour, minute=day_end.minute)
            yield start, end


def perform_autopilot_duties():
    """
    Issue timers stop or launch commands at certain times of day
    """
    from .models import Timer

    now = datetime.now(timezone.get_current_timezone()).replace(second=0, microsecond=0)
    time_now = now.time()
    if time_now in [b[0] for b in BREAKS]:
        Timer.objects.stop_for_break(now)
    elif time_now in [b[1] for b in BREAKS]:
        Timer.objects.launch_after_break(now)
