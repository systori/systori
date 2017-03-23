from datetime import date, timedelta, datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from django.utils.translation import activate
from django.core.exceptions import ValidationError
from freezegun import freeze_time

from ..company.models import Company
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer


EST = timezone.get_fixed_timezone(-5)
NOW = datetime(2014, 12, 2, 17, 58, 28, 0, EST)  # birth of Systori


@freeze_time(NOW)
class TimerTests(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company).access.first()

    def test_start(self):
        timer = Timer.start(self.worker, starting_latitude=52.5076, starting_longitude=13.3904)
        timer.refresh_from_db()
        self.assertTrue(timer.pk)
        self.assertEqual(timer.worker, self.worker)
        self.assertEqual(timer.starting_latitude, Decimal('52.5076'))
        self.assertEqual(timer.starting_longitude, Decimal('13.3904'))
        self.assertEqual(timer.started.date(), NOW.date())

    def test_start_and_stop(self):
        timer = Timer.start(worker=self.worker, stopped=NOW + timedelta(hours=2))
        self.assertFalse(timer.is_running)
        self.assertEqual(timer.stopped.date(), NOW.date())
        self.assertEqual(timer.duration, 120)

    def test_overlapping_timer_validation(self):
        activate('en')
        Timer.start(self.worker, stopped=NOW+timedelta(hours=1))
        with self.assertRaisesMessage(
                ValidationError,
                "['Overlapping timer (02.12.2014 18:03 — 02.12.2014 19:03) already exists']"):
            Timer.start(self.worker, NOW+timedelta(minutes=10))

    def test_negative_timer_validation(self):
        activate('en')
        with self.assertRaisesMessage(ValidationError, "['Timer cannot be negative']"):
            Timer.start(worker=self.worker, started=NOW, stopped=NOW - timedelta(days=2))

    def test_running_duration(self):
        timer = Timer.start(self.worker)
        self.assertEqual(timer.running_duration, 0)
        with freeze_time(NOW+timedelta(hours=1, minutes=4)):
            self.assertEqual(timer.running_duration, 64)

    def test_stop(self):
        add_hour = NOW + timedelta(hours=1, minutes=4)
        timer = Timer.start(self.worker)
        self.assertTrue(timer.is_running)
        self.assertEqual(timer.duration, 0)
        with freeze_time(add_hour):
            timer.stop(comment='test comment')
        timer.refresh_from_db()
        self.assertFalse(timer.is_running)
        self.assertEqual(timer.duration, 64)
        self.assertEqual(timer.stopped, add_hour)
        self.assertEqual(timer.comment, 'test comment')

    def test_stop_with_supplied_timestamp(self):
        timer = Timer.start(self.worker)
        stop = NOW + timedelta(hours=2)
        timer.stop(stop)
        self.assertEqual(timer.stopped, stop)
        self.assertEqual(timer.duration, 120)

    def test_stop_removes_less_than_minute_timer(self):
        timer = Timer.start(self.worker)
        self.assertTrue(Timer.objects.filter(pk=timer.pk).exists())
        with freeze_time(NOW+timedelta(seconds=30)):
            timer.stop()
        self.assertFalse(Timer.objects.filter(pk=timer.pk).exists())

    def test_stop_with_bad_kwargs(self):
        activate('en')
        timer = Timer.start(worker=self.worker)
        with self.assertRaisesMessage(TypeError, "'wtf' is not a valid field of Timer"):
            timer.stop(wtf=99)


@freeze_time(NOW)
class TimerQuerySetTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()  # type: Company
        self.worker = UserFactory(company=self.company).access.first()
        self.worker2 = UserFactory(company=self.company).access.first()

    def test_filter_today(self):
        yesterday = NOW - timedelta(days=1)
        Timer.objects.create(
            worker=self.worker,
            started=yesterday.replace(hour=9),
            stopped=yesterday.replace(hour=17)
        )
        self.assertFalse(Timer.objects.day().exists())
        timer = Timer.start(worker=self.worker)
        self.assertEqual(Timer.objects.count(), 2)
        self.assertEqual(Timer.objects.day().get(), timer)

    def test_filter_running(self):
        Timer.objects.create(
            worker=self.worker,
            started=NOW.replace(hour=9),
            stopped=NOW.replace(hour=13)
        )
        self.assertFalse(Timer.objects.running().exists())
        timer = Timer.start(self.worker)
        self.assertEqual(Timer.objects.day().count(), 2)
        self.assertEqual(Timer.objects.running().get(), timer)

    def test_create_batch(self):
        """
            October 30, 2016 is the transition from CEST to CET timezone.
            October 27, 2016 is a Thursday.
            October 31, 2016 is a Monday.
            This test will generate timers between Oct 27 and Oct 31. Which
            will verify the following features:
             - Skipping weekends.
             - Generating days across a timezone switch.
        """
        start = timezone.make_aware(datetime(2016, 10, 27, 7))
        end = timezone.make_aware(datetime(2016, 10, 31, 16))
        Timer.objects.create_batch(
            worker=self.worker, dates=(start.date(), end.date()),
            start=start.time(), stop=end.time(),
            kind=Timer.WORK, comment='Test comment'
        )
        result = Timer.objects.order_by('id').all()
        self.assertEqual(len(result), 9)  # 3 per day, two days skipped
        self.assertEqual(result[0].kind, Timer.WORK)
        self.assertEqual(result[0].comment, 'Test comment')
        self.assertEqual(result[0].started, start)  # left is UTC, right is CEST, automatically normalized for '=='
        self.assertEqual(result[0].started.hour, 5)  # different UTC from a CEST datetime
        self.assertEqual(result[6].started.hour, 6)  # different UTC from a CET datetime
        self.assertEqual(timezone.localtime(result[0].started).hour, 7)  # same local time
        self.assertEqual(timezone.localtime(result[6].started).hour, 7)  # same local time

    def test_stop_for_break(self):
        local = NOW.astimezone(timezone.get_current_timezone()).replace(minute=0, second=0)
        with freeze_time(local.replace(hour=7)):
            timer1 = Timer.start(worker=self.worker)
            timer2 = Timer.start(worker=self.worker2)
        with freeze_time(local.replace(hour=9)):
            now = timezone.now()
            Timer.objects.start_or_stop_work_breaks()
            timer1.refresh_from_db()
            timer2.refresh_from_db()
            self.assertEqual(timer1.stopped, now)
            self.assertEqual(timer2.stopped, now)
            self.assertTrue(timer1.is_auto_stopped)
            self.assertTrue(timer2.is_auto_stopped)

    def test_start_after_break(self):
        local = timezone.make_aware(datetime(2014, 12, 2))
        running_worker = UserFactory(company=self.company).access.first()
        manually_stopped_worker = UserFactory(company=self.company).access.first()
        with freeze_time(local.replace(hour=7)):
            Timer.start(worker=self.worker)
            Timer.start(worker=self.worker2)
            manually_stopped_timer = Timer.start(worker=manually_stopped_worker)

        with freeze_time(local.replace(hour=9)):
            manually_stopped_timer.stop()
            Timer.objects.start_or_stop_work_breaks()

        with freeze_time(local.replace(hour=9, minute=15)):
            running_timer_started = timezone.now()
            Timer.start(worker=running_worker)

        with freeze_time(local.replace(hour=9, minute=30)):
            Timer.objects.start_or_stop_work_breaks()
            now = timezone.now()
            timer1 = self.worker.timers.latest('started')
            timer2 = self.worker2.timers.latest('started')
            running_timer = running_worker.timers.latest('started')
            stopped_timer = manually_stopped_worker.timers.latest('started')
            self.assertEqual(timer1.started, now)
            self.assertEqual(timer2.started, now)
            self.assertTrue(timer1.is_auto_started)
            self.assertTrue(timer2.is_auto_started)
            self.assertEqual(running_timer.started, running_timer_started)
            self.assertTrue(running_timer.is_running)
            self.assertFalse(stopped_timer.is_running)


class ReportsTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker1 = UserFactory(last_name='a', company=self.company).access.first()
        self.worker2 = UserFactory(last_name='b', company=self.company).access.first()
        self.worker3 = UserFactory(last_name='c', company=self.company).access.first()
        self.worker4 = UserFactory(last_name='d', company=self.company).access.first()

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

        report = Timer.objects.get_daily_workers_report(timezone.localdate())

        self.assertEqual(report[self.worker1]['timers'][0].started, worker1_timer1.started)
        self.assertEqual(report[self.worker1]['timers'][2].stopped, worker1_timer2.stopped)
        self.assertEqual(report[self.worker1]['total'], worker1_timer1.duration + worker1_timer2.duration)

        self.assertEqual(report[self.worker2]['timers'][0].started, worker2_timer1.started)
        self.assertEqual(report[self.worker2]['timers'][2].stopped, worker2_timer2.stopped)
        self.assertEqual(report[self.worker2]['total'], worker2_timer1.duration + worker2_timer2.duration)
        self.assertEqual(report[self.worker2]['total'], worker2_timer1.duration + worker2_timer2.duration)

        self.assertEqual(report[self.worker3]['timers'][0].started, worker3_timer1.started)
        self.assertEqual(report[self.worker3]['timers'][0].stopped, None)
        self.assertEqual(report[self.worker3]['total'], worker3_timer1.running_duration)
        self.assertEqual(report[self.worker3]['total'], worker3_timer1.running_duration)
        self.assertTrue(self.worker4 in report)
