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
        self.assertEqual(report[0]['report']['start'], user1_timer1.start.strftime('%H:%M'))
        self.assertEqual(report[0]['report']['end'], user1_timer2.end.strftime('%H:%M'))
        self.assertEqual(report[0]['report']['total_duration'], '8:00')
        self.assertEqual(report[0]['report']['total'], '7:00')
        self.assertEqual(report[0]['report']['overtime'], '0:00')

        self.assertEqual(report[1]['user'], self.user2)
        self.assertEqual(report[1]['report']['start'], user2_timer1.start.strftime('%H:%M'))
        self.assertEqual(report[1]['report']['end'], user2_timer2.end.strftime('%H:%M'))
        self.assertEqual(report[1]['report']['total_duration'], '9:00')
        self.assertEqual(report[1]['report']['total'], '8:00')
        self.assertEqual(report[1]['report']['overtime'], '0:00')

        self.assertEqual(report[2]['user'], self.user3)
        self.assertEqual(report[2]['report']['start'], user3_timer1.start.strftime('%H:%M'))
        self.assertEqual(report[2]['report']['end'], '')
        self.assertEqual(report[2]['report']['total_duration'], user3_timer1.get_duration_formatted())
        self.assertEqual(
            report[2]['report']['total'], 
            utils.format_seconds(user3_timer1.get_duration_seconds() - Timer.DAILY_BREAK)
        )
        self.assertEqual(report[2]['report']['overtime'], '0:00')

        self.assertEqual(
            report[3]['report'], None
        )
