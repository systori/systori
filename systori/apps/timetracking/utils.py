from datetime import time
from operator import itemgetter
from django.contrib.auth import get_user_model


User = get_user_model()


def seconds_to_time(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return time(hours, minutes, seconds)


def format_seconds(seconds, strftime_format='%-H:%M'):
    negative = False
    if seconds < 0:
        negative = True
        seconds = abs(seconds)
    return ('-' if negative else '') + seconds_to_time(seconds).strftime(strftime_format)


def format_report_data(report):
    for row in report:
        row['date'] = row['date'].strftime('%d %b %Y')
        row['start'] = row['start'].strftime('%H:%M')
        row['end'] = row['end'].strftime('%H:%M') if row['end'] else ''
        row['total_duration'] = format_seconds(row['total_duration'])
        row['total'] = format_seconds(row['total'])
        row['overtime'] = format_seconds(row['overtime'])
        yield row


def get_report(user, year=None, month=None):
    from .models import Timer
    return format_report_data(
        Timer.objects.filter(user=user).filter_period(year, month).generate_report_data()
    )


def regroup(items, getter):
    result = {}
    for item in items:
        result[getter(item)] = item
    return result


def get_today_report(users):
    from .models import Timer

    report = format_report_data(
        Timer.objects.filter(user__in=users).filter_today().generate_report_data()
    )
    report_by_user = regroup(report, itemgetter('user_id'))
    for user in users:
        user.report = report_by_user.get(user.pk)

    return users


def get_timer_duration(user):
    from .models import Timer
    timer = Timer.objects.filter_running().filter(user=user).first()
    duration = timer.get_duration_seconds() if timer else 0
    return format_seconds(duration, '%H:%M:%S')
