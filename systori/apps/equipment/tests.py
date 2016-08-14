import json
from decimal import Decimal
from datetime import timedelta, datetime

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

    def test_save(self):
        form = EquipmentForm(data={
            'name': "Test Equipment",
            'manufacturer': "Test Manufacturer"
        })
        self.assertTrue(form.is_valid())
        equipment = form.save()
        self.assertEqual(equipment.name, "Test Equipment")
