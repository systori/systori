import random

import factory
from factory import fuzzy

from .models import EquipmentType, Equipment


class EquipmentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentType

    name = fuzzy.FuzzyText(length=15)
    rate = 1.0


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment

    equipment_type = factory.SubFactory(EquipmentTypeFactory)
    name = fuzzy.FuzzyText(length=15)
    manufacturer = fuzzy.FuzzyText(length=15)
    license_plate = "MA-ST 0815"
    number_of_seats = 5

