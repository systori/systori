from django import template
register = template.Library()

from systori.apps.project.models import DailyPlan

@register.assignment_tag
def make_dailyplan(jobsite, date):
    return DailyPlan(jobsite=jobsite, day=date)

@register.assignment_tag
def worker_dailyplans_count(worker, date):
    return worker.daily_plans.filter(day=date).count()

@register.assignment_tag
def task_dailyplans_count(task, date):
    return task.daily_plans.filter(day=date).count()