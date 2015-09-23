from django.core.urlresolvers import reverse
from django import template
register = template.Library()

from systori.apps.project.models import DailyPlan


@register.assignment_tag
def task_dailyplans_count(task, date):
    return task.dailyplans.filter(day=date).count()


@register.assignment_tag
def equipment_dailyplans_count(equipment, date):
    return equipment.dailyplans.filter(day=date).count()


@register.simple_tag
def add_daily_plan_url(project, date, jobsite=None):
    if jobsite or len(project.jobsites.all()) == 1:
        jobsite = jobsite or project.jobsites.all()[0]
        return reverse('field.dailyplan.assign-labor', args=[jobsite.id, DailyPlan(day=date).url_id])
    else:
        return reverse('field.dailyplan.pick-jobsite', args=[project.id, date.isoformat()])

@register.simple_tag
def is_assigned(plan, access):
    return DailyPlan.is_worker_assigned(plan, access)