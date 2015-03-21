from datetime import date, timedelta
from django.conf import settings
from django.core.urlresolvers import reverse


def find_next_workday(start_date):
    to_next_week = 7 - start_date.isoweekday()
    if to_next_week < 3:
        return start_date + timedelta(days=to_next_week+1)
    else:
        return start_date + timedelta(days=1)


def days_ago(ago):
    return date.today() - timedelta(days=ago)


def dailyplan_flow_next_url(dailyplan, current):
    next_step = next_dailyplan_step(current)
    return reverse('field.dailyplan.'+next_step, args=[dailyplan.jobsite.id, dailyplan.url_id])


def next_dailyplan_step(current):

    if current == 'start':
        return settings.SYSTORI_CREATE_DAILYPLAN_FLOW[0]

    idx = settings.SYSTORI_CREATE_DAILYPLAN_FLOW.index(current)

    # last element in flow, exit
    if len(settings.SYSTORI_CREATE_DAILYPLAN_FLOW) == idx+1:
        return False

    return settings.SYSTORI_CREATE_DAILYPLAN_FLOW[idx+1]