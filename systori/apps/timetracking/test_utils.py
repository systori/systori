import json
from datetime import timedelta

from freezegun import freeze_time
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer
from . import utils


User = get_user_model()
NOW = timezone.now().replace(hour=16)


class ReportsTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user1 = UserFactory(company=self.company)
        self.user2 = UserFactory(company=self.company)
        self.user3 = UserFactory(company=self.company)
        self.user4 = UserFactory(company=self.company)

    @freeze_time(NOW)
    def test_get_today_report(self):
        today = NOW.replace(hour=9)
        yesterday = today - timedelta(days=1)
        Timer.objects.create(
            user=self.user1, start=yesterday, end=yesterday + timedelta(hours=2)
        )
        Timer.objects.create(
            user=self.user1, start=yesterday + timedelta(hours=3), end=yesterday + timedelta(hours=9)
        )
        user1_timer1 = Timer.objects.create(
            user=self.user1, start=today, end=today + timedelta(hours=2)
        )
        user1_timer2 = Timer.objects.create(
            user=self.user1, start=today + timedelta(hours=3), end=today + timedelta(hours=9)
        )

        Timer.objects.create(
            user=self.user2, start=yesterday, end=yesterday + timedelta(hours=3)
        )
        Timer.objects.create(
            user=self.user2, start=yesterday + timedelta(hours=4), end=yesterday + timedelta(hours=12)
        )
        user2_timer1 = Timer.objects.create(
            user=self.user2, start=today, end=today + timedelta(hours=3)
        )
        user2_timer2 = Timer.objects.create(
            user=self.user2, start=today + timedelta(hours=3), end=today + timedelta(hours=9)
        )

        user3_timer1 = Timer.objects.create(
            user=self.user3, start=today
        )

        report = list(utils.get_today_report(User.objects.order_by('pk')))

        self.assertEqual(report[0]['user'], self.user1)
        self.assertEqual(report[0]['report']['day_start'], user1_timer1.start)
        self.assertEqual(report[0]['report']['day_end'], user1_timer2.end)
        self.assertEqual(
            report[0]['report']['total_duration'],
            user1_timer1.duration + user1_timer2.duration)
        self.assertEqual(
            report[0]['report']['total'], 
            user1_timer1.duration + user1_timer2.duration - Timer.DAILY_BREAK)
        self.assertEqual(report[0]['report']['overtime'], 0)

        self.assertEqual(report[1]['user'], self.user2)
        self.assertEqual(report[1]['report']['day_start'], user2_timer1.start)
        self.assertEqual(report[1]['report']['day_end'], user2_timer2.end)
        self.assertEqual(
            report[1]['report']['total_duration'],
            user2_timer1.duration + user2_timer2.duration)
        self.assertEqual(
            report[1]['report']['total'],
            user2_timer1.duration + user2_timer2.duration - Timer.DAILY_BREAK)
        self.assertEqual(report[1]['report']['overtime'], 0)

        self.assertEqual(report[2]['user'], self.user3)
        self.assertEqual(report[2]['report']['day_start'], user3_timer1.start)
        self.assertEqual(report[2]['report']['day_end'], None)
        self.assertEqual(report[2]['report']['total_duration'], user3_timer1.get_duration_seconds())
        self.assertEqual(
            report[2]['report']['total'], 
            user3_timer1.get_duration_seconds() - Timer.DAILY_BREAK
        )
        self.assertEqual(report[2]['report']['overtime'], 0)

        self.assertIsNone(report[3]['report'])
