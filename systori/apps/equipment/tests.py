import json
from decimal import Decimal
from django.utils import timezone

from systori.lib.testing import SystoriTestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from freezegun import freeze_time

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory

from .models import Equipment, RefuelingStop, Maintenance
from .forms import EquipmentForm, RefuelingStopForm

from ..accounting.test_workflow import create_data


class EquipmentTestCase(SystoriTestCase):

    def setUp(self):
        super().setUp()
        create_data(self)
        self.equipment = Equipment.objects.create(
            name="Test-Equiment",
            manufacturer="Mercetest",
        )
        self.client.login(username=self.user.email, password='open sesame')


class EquipmentTest(EquipmentTestCase):

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


class EquipmentFormTest(EquipmentTestCase):

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


class EquipmentCBVTest(EquipmentTestCase):

    def test_equipment_create_view(self):
        response = self.client.get(reverse('equipment.create'))
        self.assertEqual(200, response.status_code)

        data = {
            'name': "CBV create Test Equipment",
            'manufacturer': 'Bee Ehmm Double U',
            'fuel': 'diesel',
            'number_of_seats': 5
        }

        response = self.client.post(reverse('equipment.create'), data)
        self.assertEqual(302, response.status_code)

    def test_refueling_stop_create_view(self):
        response = self.client.get(reverse('refueling_stop.create', args=[self.equipment.id]))
        self.assertEqual(200, response.status_code)

        data = {
            'datetime': timezone.now(),
            'equipment': self.equipment,
            'mileage': 500,
            'liters': 50,
            'price_per_liter': 1.01
        }
        data2 = {
            'datetime': timezone.now(),
            'equipment': self.equipment,
            'mileage': 1000,
            'liters': 50,
            'price_per_liter': 1.02
        }

        response = self.client.post(reverse('refueling_stop.create', args=[self.equipment.id]), data)
        self.assertEqual(302, response.status_code)
        response = self.client.post(reverse('refueling_stop.create', args=[self.equipment.id]), data2)
        self.assertEqual(302, response.status_code)

        refueling_stop = RefuelingStop.objects.first()
        response = self.client.get(reverse('refueling_stop.update', args=[refueling_stop.id]))
        self.assertEqual(200, response.status_code)

    # def test_refueling_stop_update_view(self):
    #     refueling_stop = RefuelingStop.objects.first()
    #     response = self.client.get(reverse('refueling_stop.update', args=[refueling_stop.id]))
    #     self.assertEqual(302, response.status_code)
