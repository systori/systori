from datetime import timedelta, datetime, time

from freezegun import freeze_time
from django.test import TestCase
from django.utils import timezone

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer
from . import utils


EST = timezone.get_fixed_timezone(-5)
NOW = datetime(2014, 12, 2, 17, 58, 28, 0, EST)  # birth of Systori


class UserStatusesTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker1 = UserFactory(company=self.company).access.first()
        self.worker2 = UserFactory(company=self.company).access.first()
        self.worker3 = UserFactory(company=self.company).access.first()

    @freeze_time(NOW)
    def test_get_worker_statuses(self):
        morning = NOW.replace(hour=9)
        yesterday = morning - timedelta(days=1)
        tomorrow = morning + timedelta(days=1)

        worker1_timer = Timer.objects.create(worker=self.worker1, started=morning, kind=Timer.WORK)
        Timer.objects.create(
            worker=self.worker1, started=yesterday, stopped=yesterday + timedelta(hours=8), kind=Timer.WORK)
        Timer.objects.create(
            worker=self.worker2, started=morning, stopped=morning + timedelta(hours=2), kind=Timer.WORK)
        worker2_timer = Timer.objects.create(
            worker=self.worker2, started=NOW - timedelta(hours=1), stopped=NOW + timedelta(hours=2), kind=Timer.WORK)
        worker3_timer = Timer.objects.create(
            worker=self.worker3, started=yesterday, stopped=tomorrow, kind=Timer.VACATION)
        self.assertEqual(
            utils.get_workers_statuses(),
            {
                self.worker1.pk: worker1_timer,
                self.worker2.pk: worker2_timer,
                self.worker3.pk: worker3_timer,
            }
        )


class TimeSpanTest(TestCase):

    def setUp(self):
        self.breaks = [
            utils.BreakSpan(time(9, 00), time(9, 30)),
            utils.BreakSpan(time(12, 30), time(13, 00)),
        ]

    def assertSpan(self, expected, start, end):
        self.assertEquals([
            (time(*span[0]), time(*span[1]))
            for span in expected
        ], list(utils.get_timespans_split_by_breaks(start, end, self.breaks)))

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
        ], time(5), time(11, 30))
