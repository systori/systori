import os
import datetime, calendar, random
from datetime import timedelta
from django.utils import timezone
from freezegun import freeze_time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

from systori.apps.company.models import Company
from systori.apps.timetracking.models import Timer

c = Company.objects.get(schema=input("Company Schema:"))
c.activate()
users = c.active_users()

year = 2016
month = 7
num_days = calendar.monthrange(year, month)[1]
days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
localtz = timezone.pytz.timezone("Europe/Berlin")

Timer.objects.all().delete()

for day in days:

    for user in users:
        Timer.objects.create(
            user=user,
            start=localtz.localize(datetime.datetime.combine(day, datetime.time(7, random.randint(1, 15)))),
            end=localtz.localize(datetime.datetime.combine(day, datetime.time(16, random.randint(1, 15)))),
            kind=Timer.WORK)
