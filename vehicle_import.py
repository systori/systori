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

contractors = {
    67: "Günster & Leibfahrt",
    66: "Auto Ihm GmbH & Co.KG"
}

berlin = pytz.timezone("Europe/Berlin")

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
            equipment = Equipment.objects.create(
                name=entry['fields']['model'],
                manufacturer=entry['fields']['brand'],
                license_plate=entry['fields']['license_plate']
            )
            mapping[entry['pk']] = equipment.id
    elif 'vehicle.refuelingstop' in entry['model']:
        equipment = Equipment.objects.get(id=mapping[entry['fields']['vehicle']])
        unaware = datetime.strptime("{} {}".format(entry['fields']['date'], entry['fields']['time']), "%Y-%m-%d %X")
        aware = berlin.localize(unaware)
        RefuelingStop.objects.create(
            equipment=equipment,
            datetime=aware,
            mileage=Decimal(entry['fields']['mileage']),
            liters=Decimal(entry['fields']['liters']),
            price_per_liter=Decimal(entry['fields']['price_per_liter'])
        )
    elif 'vehicle.defect' in entry['model']:
        equipment = Equipment.objects.get(id=mapping[entry['fields']['vehicle']])
        date = datetime.strptime(entry['fields']['date'], "%Y-%m-%d").date()
        contractor = [contractors[entry['fields']['contractor']] if entry['fields']['contractor'] is not None else ''][0]
        Defect.objects.create(
            equipment=equipment,
            date=date,
            contractor=contractor,
            description=entry['fields']['description'],
            mileage=Decimal(entry['fields']['mileage']),
            cost=Decimal(entry['fields']['cost'])
        )
    else:
        print("something wrong in the neighbourhood.")
