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
    ["Sven", 30, 2016, 8, 2, 6, 47, 0, 0, location1],
    ["dam", 63, 2016, 8, 2, 6, 49, 0, 0, location1],
    ["kevin", 10, 2016, 8, 2, 6, 50, 0, 0, location1],
    ["danny", 24, 2016, 8, 2, 6, 50, 0, 0, location1],
    ["friedemann", 41, 2016, 8, 2, 6, 50, 0, 0, location1],
    ["paul", 12, 2016, 8, 2, 6, 52, 0, 0, location1],
    ["marius", 23, 2016, 8, 2, 6, 54, 0, 0, location1],
    ["luis", 64, 2016, 8, 2, 6, 55, 0, 0, location1],
    ["albin", 65, 2016, 8, 2, 6, 55, 0, 0, location1],
    ["stephan", 17, 2016, 8, 2, 7, 1, 0, 0, location1],
    ["marcello", 46, 2016, 8, 2, 7, 1, 0, 0, location1],
    ["oleg", 18, 2016, 8, 2, 7, 23, 0, 0, location_oleg],
]



for data in user_timers:
    user = User.objects.get(id=data[1])
    Timer.objects.create(user=user, date=today,
                         start=datetime.datetime(data[2], data[3], data[4], data[5], data[6], data[7], data[8],tzinfo=tz),
                         start_latitude=data[9][0],
                         start_longitude=data[9][1])