import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
import pytz
from django.utils import timezone
import datetime

django.setup()

from systori.apps.user.models import User
from systori.apps.company.models import *
from systori.apps.timetracking.models import Timer

company = Company.objects.get(schema="mehr-handwerk")
company.activate()
today = timezone.now().date()
tz = pytz.timezone('Europe/Berlin')

location1 = [49.516043, 8.454014]
location_oleg = [49.507978, 8.529639]

user_timers = [
    25,
    61,
    44,
    7,
    19,
    22,
    30,
    63,
    10,
    24,
    41,
    12,
    23,
    64,
    65,
    17,
    46,
    18,
]



for id in user_timers:
    user = User.objects.get(id=id)
    timer = Timer.objects.filter(user=user).last()
    timer.start -= datetime.timedelta(hours=1, minutes=7)
    if timer.end:
        timer.end -= datetime.timedelta(hours=1, minutes=7)
    timer.save()