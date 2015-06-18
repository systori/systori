from datetime import date, timedelta
from django.conf import settings
from django.core.urlresolvers import reverse


def find_next_workday(start_date):
    to_next_week = 7 - start_date.isoweekday()
    if to_next_week < 3:
        return start_date + timedelta(days=to_next_week + 1)
    else:
        return start_date + timedelta(days=1)


def get_workday(start_date):
    if start_date.weekday() < 5:
        return start_date
    return find_next_workday(start_date)


def days_ago(ago):
    return date.today() - timedelta(days=ago)


def delete_me_dailyplan_flow_next_url(dailyplan, current):
    next_step = next_dailyplan_step(current)
    return reverse('field.dailyplan.' + next_step, args=[dailyplan.jobsite.id, dailyplan.url_id]) + \
           '?origin=' + reverse('field.project', args=[dailyplan.jobsite.project.id, dailyplan.day.isoformat()])
