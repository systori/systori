from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from systori.lib.testing import ClientTestCase
from .models import Equipment, RefuelingStop, Maintenance
from .factories import EquipmentFactory


class EquipmentTestCase(ClientTestCase):
    def setUp(self):
        # ToDo: use EquipmentFactory
        super().setUp()
        self.equipment = Equipment.objects.create(
            active=True,
            name="Test Equipment0",
            manufacturer="Mercetest",
            license_plate="MA-ST 0",
            number_of_seats=2,
            fuel="diesel",
        )


class RefuelingStopTest(EquipmentTestCase):
    def test_average_consumption_and_mileage(self):
        stop1 = RefuelingStop.objects.create(
            datetime=timezone.now(),
            equipment=self.equipment,
            mileage=500,
            liters=50,
            price_per_liter=1.01,
        )
        stop2 = RefuelingStop.objects.create(
            datetime=timezone.now(),
            equipment=self.equipment,
            mileage=1000,
            liters=25,
            price_per_liter=1.02,
        )
        self.assertEqual(stop1.average_consumption, 10)
        self.assertEqual(stop2.average_consumption, 5)

        average_consumption = Equipment.objects.first().average_consumption
        self.assertEqual(average_consumption, 7.5)

        mileage = Equipment.objects.first().mileage
        self.assertEqual(1000, mileage)

        Maintenance.objects.create(
            equipment=self.equipment,
            date=timezone.now().date(),
            mileage=1500,
            description="Test Maintenance, very Expensive",
            contractor="Steve Jobs",
            cost=134598.23,
        )
        mileage = Equipment.objects.first().mileage
        self.assertEqual(mileage, 1500)

        equipment2 = Equipment.objects.create(
            active=True,
            name="Test Equipment0",
            manufacturer="Mercetest",
            license_plate="MA-ST 0",
            number_of_seats=2,
            fuel="diesel",
        )
        self.assertEqual(equipment2.average_consumption, _("unknown"))

    def test_validation_and_cascade_save(self):
        # this method tests the custom validation and the cascade_save flag
        response = self.client.get(
            reverse("refueling_stop.create", args=[self.equipment.id])
        )
        self.assertEqual(response.status_code, 200)

        data = {
            "datetime": "2016-08-11 07:00:00",
            "equipment": self.equipment.id,
            "mileage": 500,
            "liters": 50,
            "price_per_liter": 1.01,
        }
        data2 = {
            "datetime": "2016-08-12 07:00:00",
            "equipment": self.equipment.id,
            "mileage": 1000,
            "liters": 50,
            "price_per_liter": 1.02,
        }

        response = self.client.post(
            reverse("refueling_stop.create", args=[self.equipment.id]), data
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            reverse("refueling_stop.create", args=[self.equipment.id]), data2
        )
        self.assertEqual(response.status_code, 302)

        refueling_stop = RefuelingStop.objects.first()
        data = {
            "datetime": "2016-08-11 07:00:00",
            "equipment": self.equipment.id,
            "mileage": 520,
            "liters": 50,
            "price_per_liter": 1.01,
        }

        response = self.client.post(
            reverse(
                "refueling_stop.update", args=[self.equipment.id, refueling_stop.id]
            ),
            data,
        )
        self.assertEqual(response.status_code, 302)

        refueling_stop = RefuelingStop.objects.last()
        self.assertEqual(refueling_stop.distance, 480.00)

        data = {
            "datetime": "2016-08-12 07:00:00",
            "equipment": self.equipment.id,
            "mileage": 519,
            "liters": 50,
            "price_per_liter": 1.02,
        }
        response = self.client.post(
            reverse(
                "refueling_stop.update", args=[self.equipment.id, refueling_stop.id]
            ),
            data,
        )
        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["mileage"],
            [_("you must enter a higher mileage than the older refueling stop.")],
        )

        refueling_stop = RefuelingStop.objects.first()

        data = {
            "datetime": "2016-08-11 07:00:00",
            "equipment": self.equipment.id,
            "mileage": 1001,
            "liters": 50,
            "price_per_liter": 1.01,
        }

        response = self.client.post(
            reverse(
                "refueling_stop.update", args=[self.equipment.id, refueling_stop.id]
            ),
            data,
        )
        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["mileage"],
            [_("you must enter a smaller mileage than the younger refueling stop.")],
        )


class EquipmentListViewTest(EquipmentTestCase):
    def test_kwarg_queryset_filter(self):
        response = self.client.get(reverse("equipment.list"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("equipment.list", kwargs={"active_filter": "active"})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("equipment.list", kwargs={"active_filter": "passive"})
        )
        self.assertEqual(response.status_code, 200)


class EquipmentViewTest(EquipmentTestCase):
    def test_render(self):
        response = self.client.get(reverse("equipment.view", args=[self.equipment.id]))
        self.assertEqual(response.status_code, 200)
