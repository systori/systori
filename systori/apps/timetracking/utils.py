from datetime import time, timedelta
from operator import itemgetter

from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


WORK_DAY = timedelta(hours=8).total_seconds()
HOLIDAYS_PER_MONTH = WORK_DAY * 1.5


def regroup(items, getter):
    result = {}
    for item in items:
        result[getter(item)] = item
    return result


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


def format_days(seconds):
    return '{:.1f}'.format(seconds / WORK_DAY)


def format_dashboard_report_data(report):
    for row in report:
        row['date'] = row['date'].strftime('%d %b %Y')
        row['day_start'] = row['day_start'].strftime('%H:%M')
        row['day_end'] = row['day_end'].strftime('%H:%M') if row['day_end'] else ''
        row['total_duration'] = format_seconds(row['total_duration'])
        row['total'] = format_seconds(row['total'])
        row['overtime'] = format_seconds(row['overtime'])
        yield row


### Reports


def get_user_dashboard_report(user):
    from .models import Timer
    report = format_dashboard_report_data(
        Timer.objects.filter(user=user, kind=Timer.WORK).filter_date().generate_daily_users_report()
    )
    return report


def get_user_monthly_report(user, period):
    from .models import Timer
    period = period or timezone.now()

    holidays_used = get_holidays_duration(user, period.year, period.month)
    report = Timer.objects.filter(user=user).generate_user_report_data(period)
    overtime = sum(r.get('overtime', 0) for day in report.values() for r in day)
    return {
        'holidays_used': format_days(holidays_used),
        'holidays_available': format_days(HOLIDAYS_PER_MONTH - holidays_used),
        'rows': report,
        'overtime': overtime,
    }


def get_holidays_duration(user, year, month):
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
