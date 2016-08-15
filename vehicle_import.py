import os
import json
from decimal import Decimal
from datetime import datetime


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
import pytz

django.setup()

from systori.apps.company.models import Company
from systori.apps.equipment.models import Equipment, RefuelingStop, Defect

c = Company.objects.get(schema="mehr-handwerk").activate()

file = open("vehicle_data.json")
data = json.loads(file.read())

mapping = {
    16: 4,
    10: 5,
    19: 13,
    14: 3,
    7: 8,
    3: 7,
    12: 9,
    6: 10,
    21: 6,
    13: 2,
    4: 12,
    17: 11,
    8: 1
}

data_left = []

for entry in data:
    if 'vehicle.vehicle' in entry['model']:
        try:
            equipment = Equipment.objects.get(id=mapping[entry['pk']])
        except KeyError:
            equipment = None
        if equipment is not None:
            equipment.license_plate = entry['fields']['license_plate']
            equipment.manufacturer = entry['fields']['brand']
            equipment.name += " {}".format(entry['fields']['model'])
            equipment.save()
        else:
            data_left.append(entry)
    elif 'vehicle.refuelingstop' in entry['model']:
        try:
            equipment = Equipment.objects.get(id=mapping[entry['pk']])
        except KeyError:
            equipment = None
        if equipment is not None:
            unaware = datetime.strptime("{} {}".format(entry['fields']['date'], entry['fields']['time']), "%Y-%m-%d %X")
            aware = unaware.replace(tzinfo=pytz.timezone("CET"))
            print(entry['pk'])
            RefuelingStop.objects.create(
                equipment=equipment,
                datetime=aware,
                mileage=Decimal("{:06.2f}".format(entry['fields']['mileage'])),
                liters=Decimal("{:03.2f}".format(entry['fields']['liters'])),
                price_per_liter=Decimal("{:03.3f}".format(entry['fields']['price_per_liter']))
            )
        else:
            data_left.append(entry)

for entry in data_left:
    print(entry)