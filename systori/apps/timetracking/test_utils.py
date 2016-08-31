import json
from datetime import timedelta, datetime, time

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


class RoundToNearestMultipleTest(TestCase):

    def test_round_seconds(self):
        self.assertEquals(0, utils.round_to_nearest_multiple(1))
        self.assertEquals(0, utils.round_to_nearest_multiple(17))
        self.assertEquals(36, utils.round_to_nearest_multiple(18))
        self.assertEquals(36, utils.round_to_nearest_multiple(35))
        self.assertEquals(252, utils.round_to_nearest_multiple(250))
        self.assertEquals(216, utils.round_to_nearest_multiple(230))


class ReportsTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user1 = UserFactory(company=self.company)
        self.user2 = UserFactory(company=self.company)
        self.user3 = UserFactory(company=self.company)
        self.user4 = UserFactory(company=self.company)

    @freeze_time(NOW)
    def test_get_daily_users_report(self):
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
            user=self.user2, start=today + timedelta(hours=6), end=today + timedelta(hours=9)
        )

        user3_timer1 = Timer.objects.create(
            user=self.user3, start=today
        )

        report = utils.get_daily_users_report(User.objects.order_by('pk'))

        self.assertEqual(report[self.user1]['day_start'], user1_timer1.start)
        self.assertEqual(report[self.user1]['day_end'], user1_timer2.end)
        self.assertEqual(
            report[self.user1]['total_duration'],
            user1_timer1.duration + user1_timer2.duration)
        self.assertEqual(
            report[self.user1]['total'], 
            user1_timer1.duration + user1_timer2.duration - Timer.DAILY_BREAK)
        self.assertEqual(report[self.user1]['overtime'], -3600)

        self.assertEqual(report[self.user2]['day_start'], user2_timer1.start)
        self.assertEqual(report[self.user2]['day_end'], user2_timer2.end)
        self.assertEqual(
            report[self.user2]['total_duration'],
            user2_timer1.duration + user2_timer2.duration)
        self.assertEqual(
            report[self.user2]['total'],
            user2_timer1.duration + user2_timer2.duration - Timer.DAILY_BREAK)
        self.assertEqual(report[self.user2]['overtime'], -10800)

        self.assertEqual(report[self.user3]['day_start'], user3_timer1.start)
        self.assertEqual(report[self.user3]['day_end'], None)
        self.assertEqual(report[self.user3]['total_duration'], user3_timer1.get_duration_seconds())
        self.assertEqual(
            report[self.user3]['total'], 
            user3_timer1.get_duration_seconds() - Timer.DAILY_BREAK
        )
        self.assertEqual(report[self.user3]['overtime'], -7200)

        self.assertFalse(report[self.user4]['total'])


class UserStatusesTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user1 = UserFactory(company=self.company)
        self.user2 = UserFactory(company=self.company)
        self.user3 = UserFactory(company=self.company)

    @freeze_time(NOW)
    def test_get_user_statuses(self):
        morning = NOW.replace(hour=9)
        yesterday = morning - timedelta(days=1)
        tomorrow = morning + timedelta(days=1)

        user1_timer = Timer.objects.create(user=self.user1, start=morning, kind=Timer.WORK)
        Timer.objects.create(
            user=self.user1, start=yesterday, end=yesterday + timedelta(hours=8), kind=Timer.WORK)
        Timer.objects.create(
            user=self.user2, start=morning, end=morning + timedelta(hours=2), kind=Timer.WORK)
        user2_timer = Timer.objects.create(
            user=self.user2, start=NOW - timedelta(hours=1), end=NOW + timedelta(hours=2), kind=Timer.WORK)
        user3_timer = Timer.objects.create(
            user=self.user3, start=yesterday, end=tomorrow, kind=Timer.HOLIDAY)
        self.assertEqual(
            utils.get_users_statuses(User.objects.all()),
            {
                self.user1.pk: [user1_timer],
                self.user2.pk: [user2_timer],
                self.user3.pk: [user3_timer],
            }
        )


class TimeSpanTest(TestCase):

    def setUp(self):
        self.days = [datetime(2016, 8, 30)]

    def t(self, hour=0, minute=0, second=0):
        return self.days[0].replace(hour=hour, minute=minute, second=second)

    def assertSpan(self, expected, start, end):
        self.assertEquals([
            (self.t(*span[0]), self.t(*span[1]))
            for span in expected
        ], list(utils.get_timer_spans(start, end, self.days)))

    def test_simple(self):
        self.assertSpan([
            ((7, 00),  (9, 00)),
            ((9, 30), (12, 30)),
            ((13, 00), (16, 00))
         ], time(7), time(16))

    def test_simple_overtime(self):
        self.assertSpan([
            ((7, 00),  (9, 00)),
            ((9, 30), (12, 30)),
            ((13, 00), (18, 00))
         ], time(7), time(18))

    def test_start_at_break(self):
        self.assertSpan([
            ((9, 30), (12, 30)),
            ((13, 00), (16, 00))
        ], time(9), time(16))

    def test_late_start(self):
        self.assertSpan([
            ((14, 00), (16, 00))
        ], time(14), time(16))

    def test_early_finish(self):
        self.assertSpan([
            ((8, 00), (9, 00)),
            ((9, 30), (10, 00)),
        ], time(8), time(10))

    def test_early_break_only(self):
        self.assertSpan([], time(9), time(9, 30))

    def test_late_break_only(self):
        self.assertSpan([], time(12, 30), time(13))

    def test_early_start_early_break(self):
        self.assertSpan([
            ((5, 00), (9, 00)),
            ((9, 30), (11, 30))
        ], time(5), time(11))
