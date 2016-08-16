import json
from decimal import Decimal
from django.utils import timezone

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from freezegun import freeze_time

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory

from .models import Equipment, RefuelingStop, Defect
from .forms import EquipmentForm, RefuelingStopForm


class EquipmentTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        Equipment.objects.create(
            name="Test-Equiment",
            manufacturer="Mercetest",
        )

    def test_equipment_create(self):
        equipment = Equipment.objects.first()
        self.assertTrue(equipment.pk)

    def test_refueling_stop_create(self):
        equipment = Equipment.objects.first()
        refueling_stop = RefuelingStop.objects.create(
            equipment=equipment,
            mileage=Decimal(100),
            liters=Decimal(10),
            price_per_liter=Decimal(1)
        )
        self.assertEqual(refueling_stop.average_consumption, Decimal(10))


class EquipmentFormTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.equipment = Equipment.objects.create(
            name="Test-Equiment",
            manufacturer="Mercetest",
        )

    def test_EquipmentForm_create(self):
        form = EquipmentForm(data={
            'active': True,
            'name': "Test Equipment",
            'manufacturer': "Test Manufacturer",
            'license_plate': "MA-ST 1",
            'number_of_seats': 5,
            'fuel': 'diesel'
        })
        self.assertTrue(form.is_valid(), form.errors)
        equipment = form.save()
        self.assertEqual(equipment.name, "Test Equipment")

    def test_RefuelingStopForm_create(self):
        form = RefuelingStopForm(data={
            'equipment': self.equipment.id,
            'mileage': 500,
            'liters': 50,
            'price_per_liter': 1.01,
            'datetime': timezone.now()
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_refuelung_stop_multiple(self):
        stop1 = RefuelingStop.objects.create(
            datetime=timezone.now(),
            equipment=self.equipment,
            mileage=500,
            liters=50,
            price_per_liter=1.01
        )
        stop2 = RefuelingStop.objects.create(
            datetime=timezone.now(),
            equipment=self.equipment,
            mileage=1000,
            liters=50,
            price_per_liter=1.02
        )
        self.assertEqual(stop2.average_consumption, stop1.average_consumption)