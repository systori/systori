from datetime import timedelta, datetime
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
        self.assertFalse(Timer.objects.filter_today().exists())
        timer = Timer.start(worker=self.worker)
        self.assertEqual(Timer.objects.count(), 2)
        self.assertEqual(Timer.objects.filter_today().get(), timer)

    def test_filter_running(self):
        Timer.objects.create(
            worker=self.worker,
            started=NOW.replace(hour=9),
            stopped=NOW.replace(hour=13)
        )
        self.assertFalse(Timer.objects.filter_running().exists())
        timer = Timer.start(self.worker)
        self.assertEqual(Timer.objects.filter_today().count(), 2)
        self.assertEqual(Timer.objects.filter_running().get(), timer)

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
        tz = self.company.timezone
        start = tz.localize(datetime(2016, 10, 27, 7))
        end = tz.localize(datetime(2016, 10, 31, 16))
        Timer.objects.create_batch(
            worker=self.worker, started=start, stopped=end,
            kind=Timer.WORK, comment='Test comment'
        )
        result = Timer.objects.order_by('id').all()
        self.assertEqual(len(result), 9)  # 3 per day, two days skipped
        self.assertEqual(result[0].kind, Timer.WORK)
        self.assertEqual(result[0].comment, 'Test comment')
        self.assertEqual(result[0].started, start)  # left is UTC, right is CEST, automatically normalized for '=='
        self.assertEqual(result[0].started.hour, 5)  # different UTC from a CEST datetime
        self.assertEqual(result[6].started.hour, 6)  # different UTC from a CET datetime
        self.assertEqual(result[0].started.astimezone(tz).hour, 7)  # same local time
        self.assertEqual(result[6].started.astimezone(tz).hour, 7)  # same local time

    def test_stop_for_break(self):
        with freeze_time('2016-08-16 07:00'):
            timer1 = Timer.start(worker=self.worker)
            timer2 = Timer.start(worker=self.worker2)
        with freeze_time('2016-08-16 09:00'):
            now = timezone.now()
            stopped_count = Timer.objects.stop_for_break()
            timer1.refresh_from_db()
            timer2.refresh_from_db()
            self.assertEqual(stopped_count, 2)
            self.assertEqual(timer1.stopped, now)
            self.assertEqual(timer2.stopped, now)
            self.assertTrue(timer1.is_auto_stopped)
            self.assertTrue(timer2.is_auto_stopped)

    def test_launch_after_break(self):
        running_worker = UserFactory(company=self.company).access.first()
        manually_stopped_worker = UserFactory(company=self.company).access.first()
        with freeze_time('2016-08-16 07:00'):
            Timer.start(worker=self.worker)
            Timer.start(worker=self.worker2)
            manually_stopped_timer = Timer.start(worker=manually_stopped_worker)

        with freeze_time('2016-08-16 09:00'):
            manually_stopped_timer.stop()
            Timer.objects.stop_for_break()

        with freeze_time('2016-08-16 09:15'):
            running_timer_started = timezone.now()
            Timer.start(worker=running_worker)

        with freeze_time('2016-08-16 09:30'):
            Timer.objects.launch_after_break()
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
