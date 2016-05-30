import json
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer


class TimerTest(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)

    def test_launch(self):
        timer = Timer.launch(self.user)
        self.assertTrue(timer.pk)
        self.assertEqual(timer.user, self.user)
        self.assertTrue(timer.is_running)

    def test_no_two_timers(self):
        Timer.launch(self.user)
        with self.assertRaises(ValidationError):
            Timer.launch(self.user)

    def test_get_duration(self):
        timer = Timer.launch(self.user)
        self.assertEqual(
            timer.get_duration(now=timezone.now() + timedelta(hours=4)),
            [4, 0, 0]
        )

    def test_stop(self):
        timer = Timer.launch(self.user)
        timer.stop()
        self.assertTrue(timer.end)

    def test_to_dict(self):
        timer = Timer.launch(self.user)
        self.assertEqual(
            timer.to_dict(),
            {'duration': timer.get_duration()}
        )


class TimerQuerySetTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.user2 = UserFactory(company=self.company)

    def test_filter_today(self):

        now = timezone.now().replace(hour=9)
        yesterday = now - timedelta(days=1)
        Timer.objects.create(
            user=self.user,
            start=yesterday,
            end=yesterday + timedelta(hours=8)
        )

        timer = Timer.launch(self.user)
        self.assertEqual(
            Timer.objects.filter_today().get(),
            Timer.objects.get(pk=timer.pk)
        )

    def test_filter_running(self):
        now = timezone.now().replace(hour=9)
        yesterday = now - timedelta(days=1)
        Timer.objects.create(
            user=self.user,
            start=yesterday,
            end=yesterday + timedelta(hours=8)
        )

        timer = Timer.launch(self.user)
        self.assertEqual(
            Timer.objects.filter_running().get(),
            Timer.objects.get(pk=timer.pk)
        )
