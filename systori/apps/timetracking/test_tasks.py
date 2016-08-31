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
        user1 = UserFactory(company=company1)
        Timer.objects.create(user=user1, start=timezone.now() - timedelta(hours=7))

        company2 = CompanyFactory(schema='testcompany2')
        user2 = UserFactory(company=company2)
        Timer.objects.create(user=user2, start=timezone.now() - timedelta(hours=5))

        tasks.stop_abandoned_timers()
        company1.activate()
        self.assertFalse(Timer.objects.filter_running().exists())
        company2.activate()
        self.assertFalse(Timer.objects.filter_running().exists())
