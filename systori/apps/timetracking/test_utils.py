from unittest import skip
from unittest.mock import patch
from datetime import timedelta, datetime, time

from freezegun import freeze_time
from django.test import TestCase
from django.utils import timezone

from systori.lib.templatetags.customformatting import tosexagesimalhours
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer
from . import utils


NOW = timezone.now().replace(hour=16)


class UtilsTest(TestCase):

    def test_tosexagesimalhours(self):
        self.assertEqual(tosexagesimalhours(7*60+56), '7:56')
        self.assertEqual(tosexagesimalhours(5), '0:05')

    def test_get_timetracking_workers(self):
        company = CompanyFactory()
        worker1 = UserFactory(company=company).access.first()
        worker2 = UserFactory(company=company).access.first()
        worker1.is_timetracking_enabled = False
        worker1.save()
        timetracking_workers = utils.get_timetracking_workers(company)
        self.assertNotIn(worker1, timetracking_workers)
        self.assertIn(worker2, timetracking_workers)


class ReportsTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker1 = UserFactory(company=self.company).access.first()
        self.worker2 = UserFactory(company=self.company).access.first()
        self.worker3 = UserFactory(company=self.company).access.first()
        self.worker4 = UserFactory(company=self.company).access.first()

    @freeze_time(NOW)
    def test_get_daily_workers_report(self):
        today = NOW.replace(hour=9)
        yesterday = today - timedelta(days=1)
        Timer.objects.create(
            worker=self.worker1, started=yesterday, stopped=yesterday + timedelta(hours=2)
        )
        Timer.objects.create(
            worker=self.worker1, started=yesterday + timedelta(hours=3), stopped=yesterday + timedelta(hours=9)
        )
        worker1_timer1 = Timer.objects.create(
            worker=self.worker1, started=today, stopped=today + timedelta(hours=2)
        )
        worker1_timer2 = Timer.objects.create(
            worker=self.worker1, started=today + timedelta(hours=3), stopped=today + timedelta(hours=8)
        )

        Timer.objects.create(
            worker=self.worker2, started=yesterday, stopped=yesterday + timedelta(hours=3)
        )
        Timer.objects.create(
            worker=self.worker2, started=yesterday + timedelta(hours=4), stopped=yesterday + timedelta(hours=12)
        )
        worker2_timer1 = Timer.objects.create(
            worker=self.worker2, started=today, stopped=today + timedelta(hours=3)
        )
        worker2_timer2 = Timer.objects.create(
            worker=self.worker2, started=today + timedelta(hours=6), stopped=today + timedelta(hours=9)
        )

        worker3_timer1 = Timer.objects.create(
            worker=self.worker3, started=today
        )

        report = utils.get_daily_workers_report(self.company.workers.order_by('pk'))

        self.assertEqual(report[self.worker1]['timers'][0].started, worker1_timer1.started)
        self.assertEqual(report[self.worker1]['timers'][1].stopped, worker1_timer2.stopped)
        self.assertEqual(
            report[self.worker1]['total_duration'],
            worker1_timer1.duration + worker1_timer2.duration)
        self.assertEqual(report[self.worker1]['overtime'], -60)

        self.assertEqual(report[self.worker2]['timers'][0].started, worker2_timer1.started)
        self.assertEqual(report[self.worker2]['timers'][1].stopped, worker2_timer2.stopped)
        self.assertEqual(
            report[self.worker2]['total_duration'],
            worker2_timer1.duration + worker2_timer2.duration)
        self.assertEqual(
            report[self.worker2]['total_duration'],
            worker2_timer1.duration + worker2_timer2.duration)
        self.assertEqual(report[self.worker2]['overtime'], -120)

        self.assertEqual(report[self.worker3]['timers'][0].started, worker3_timer1.started)
        self.assertEqual(report[self.worker3]['timers'][0].stopped, None)
        self.assertEqual(report[self.worker3]['total_duration'], worker3_timer1.running_duration)
        self.assertEqual(report[self.worker3]['total_duration'], worker3_timer1.running_duration)
        self.assertEqual(report[self.worker3]['overtime'], -60)
        self.assertFalse(report[self.worker4]['total_duration'])


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
            utils.get_workers_statuses(self.company.workers.all()),
            {
                self.worker1.pk: [worker1_timer],
                self.worker2.pk: [worker2_timer],
                self.worker3.pk: [worker3_timer],
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


class AutoPilotTest(TestCase):

    @skip
    @patch.object(Timer, 'objects')
    def test_perform_autopilot_duties(self, manager_mock):
        company = CompanyFactory()
        breaks, tz = company.breaks, company.timezone
        round_now = lambda: datetime.now(tz).replace(second=0, microsecond=0)
        offset = -tz.utcoffset(datetime.now()).total_seconds() / 60 / 60

        with freeze_time('2016-08-16 08:55:59', tz_offset=offset):
            utils.perform_autopilot_duties(breaks, tz)
            self.assertFalse(manager_mock.stop_for_break.mock_calls)
            self.assertFalse(manager_mock.launch_after_break.mock_calls)
        manager_mock.stop_for_break.reset_mock()

        with freeze_time('2016-08-16 09:00:45', tz_offset=offset):
            utils.perform_autopilot_duties(breaks, tz)
            manager_mock.stop_for_break.assert_called_once_with(round_now())
            self.assertFalse(manager_mock.launch_after_break.mock_calls)
        manager_mock.stop_for_break.reset_mock()

        with freeze_time('2016-08-16 09:15:15', tz_offset=offset):
            utils.perform_autopilot_duties(breaks, tz)
            self.assertFalse(manager_mock.stop_for_break.mock_calls)
            self.assertFalse(manager_mock.launch_after_break.mock_calls)
        manager_mock.stop_for_break.reset_mock()

        with freeze_time('2016-08-16 09:30:01', tz_offset=offset):
            utils.perform_autopilot_duties(breaks, tz)
            self.assertFalse(manager_mock.stop_for_break.mock_calls)
            manager_mock.launch_after_break.assert_called_once_with(round_now())
        manager_mock.stop_for_break.reset_mock()
