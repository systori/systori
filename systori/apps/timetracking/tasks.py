from celery import task
from celery.schedules import crontab

from systori.apps.company.models import Company
from .models import Timer
from .utils import perform_autopilot_duties


@task.periodic_task(run_every=crontab(hour=0, minute=00))
def stop_abandoned_timers():
    for company in Company.objects.all():
        company.activate()
        Timer.objects.stop_abandoned()

@task.periodic_task(run_every=crontab(minute='*'))
def launch_autopilot():
    for company in Company.objects.all():
        company.activate()
        perform_autopilot_duties()
