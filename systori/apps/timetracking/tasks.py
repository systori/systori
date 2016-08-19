from celery import task
from celery.schedules import crontab

from systori.apps.company.models import Company
from .models import Timer


@task.periodic_task(run_every=crontab(hour=0, minute=00))
def stop_abandoned_timers():
    for company in Company.objects.all():
        company.activate()
        Timer.objects.stop_abandoned()
