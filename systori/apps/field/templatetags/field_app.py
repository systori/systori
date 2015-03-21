from django.core.urlresolvers import reverse
from django import template
register = template.Library()

from systori.apps.project.models import DailyPlan
from systori.apps.field.utils import dailyplan_flow_next_url


@register.assignment_tag
def worker_dailyplans_count(worker, date):
    return worker.dailyplans.filter(day=date).count()


@register.assignment_tag
def task_dailyplans_count(task, date):
    return task.dailyplans.filter(day=date).count()

@register.simple_tag
def add_daily_plan_url(project, date):
    if project.jobsites.count() == 1:
        jobsite = project.jobsites.first()
        return dailyplan_flow_next_url(DailyPlan(jobsite=jobsite, day=date), 'start')
    else:
        return reverse('field.dailyplan.pick-jobsite', args=[project.id, date.isoformat()])