from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer
from . import tasks


class TasksTest(TestCase):

    @freeze_time('2016-08-16 18:30')
    def test_stop_abandoned_timers(self):
        company1 = CompanyFactory()
        worker1 = UserFactory(company=company1).access.first()
        Timer.objects.create(worker=worker1, start=timezone.now() - timedelta(hours=7))

        company2 = CompanyFactory(schema='testcompany2')
        worker2 = UserFactory(company=company2).access.first()
        Timer.objects.create(worker=worker2, start=timezone.now() - timedelta(hours=5))

        tasks.stop_abandoned_timers()
        company1.activate()
        self.assertFalse(Timer.objects.filter_running().exists())
        company2.activate()
        self.assertFalse(Timer.objects.filter_running().exists())
