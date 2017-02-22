from celery import task
from celery.schedules import crontab

from systori.apps.company.models import Company
from .models import Timesheet
from datetime import date


@task.periodic_task(run_every=crontab(hour=22, minute=0))
def generate_timesheets():
    today = date.today()
    for company in Company.objects.all():
        company.activate()
        Timesheet.generate(today.year, today.month)
