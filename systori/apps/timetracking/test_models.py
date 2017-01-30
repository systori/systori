import json
import pytz
from datetime import timedelta, datetime

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from freezegun import freeze_time

from ..company.models import Company
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer


NOW = timezone.now().replace(hour=12)


class TimerTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company).access.first()

    def test_launch(self):
        timer = Timer.launch(self.worker)
        self.assertTrue(timer.pk)
        self.assertEqual(timer.worker, self.worker)
        self.assertTrue(timer.is_running)

    def test_launch_with_kwargs(self):
        timer = Timer.launch(self.worker, start_latitude=52.5076, start_longitude=13.3904)
        self.assertTrue(timer.pk)
        self.assertEqual(timer.worker, self.worker)
        self.assertEqual(timer.start_latitude, 52.5076)
        self.assertEqual(timer.start_longitude, 13.3904)
        self.assertTrue(timer.is_running)

    def test_no_two_timers(self):
        Timer.launch(self.worker)
        with self.assertRaises(ValidationError):
            Timer.launch(self.worker)

    def test_get_duration(self):
        timer = Timer.launch(self.worker)
        self.assertEqual(
            timer.get_duration(now=timezone.now() + timedelta(hours=4)),
            [4, 0, 0]
        )

    def test_stop(self):
        timer = Timer.launch(self.worker)
        timer.stop(ignore_short_duration=False)
        self.assertTrue(timer.end)

    @freeze_time('2016-08-16 18:30')
    def test_stop_with_supplied_timestamp(self):
        timer = Timer.launch(self.worker)
        timer.stop(end=timezone.now() + timedelta(hours=2))
        self.assertEqual(timer.end.strftime('%H:%M'), '20:30')

    def test_stop_with_extra_params(self):
        with freeze_time(timezone.now() - timedelta(hours=3)):
            timer = Timer.launch(self.worker)
        timer.stop(is_auto_stopped=True, comment='test comment')
        timer.refresh_from_db()
        self.assertTrue(timer.is_auto_stopped)
        self.assertEqual(timer.comment, 'test comment')

    def test_stop_zero_timer_ignores_it(self):
        timer = Timer.launch(self.worker)
        timer.stop()
        self.assertFalse(Timer.objects.filter(pk=timer.pk).exists())

    def test_to_dict(self):
        timer = Timer.launch(self.worker)
        self.assertEqual(
            timer.to_dict(),
            {'duration': timer.get_duration()}
        )

    @freeze_time(NOW)
    def test_save_regular_timer(self):
        timer = Timer(worker=self.worker)
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertIsNone(timer.end)

        with self.assertRaises(ValidationError):
            timer = Timer(worker=self.worker)
            timer.clean()

    @freeze_time(NOW)
    def test_save_public_holiday_timer(self):
        now = timezone.now()
        start = now.replace(hour=12, minute=30)
        end = now.replace(hour=16, minute=45)
        expected_start = now.replace(hour=7, minute=0, second=0, microsecond=0)
        expected_end = now.replace(hour=15, minute=0, second=0, microsecond=0)
        timer = Timer(worker=self.worker, kind=Timer.PUBLIC_HOLIDAY, start=start, end=end)
        timer.save()
        self.assertEqual(timer.start, expected_start)
        self.assertEqual(timer.end, expected_end)
        self.assertEqual(timer.date, now.date())
        self.assertEqual(timer.duration, 60 * 60 * 8)

    @freeze_time(NOW)
    def test_save_with_end(self):
        timer = Timer(worker=self.worker, end=NOW + timedelta(hours=2))
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertEqual(timer.duration, 60 * 60 * 2)

    @freeze_time(NOW)
    def test_save_with_duration(self):
        timer = Timer(worker=self.worker, duration=60 * 60 * 2)
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertEqual(timer.end, NOW + timedelta(hours=2))

    @freeze_time(NOW)
    def test_save_correction_timer(self):
        timer = Timer(worker=self.worker, duration=60 * 60 * 2, kind=Timer.CORRECTION)
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.end, NOW + timedelta(hours=2))
        self.assertEqual(timer.date, NOW.date())

    @freeze_time(NOW)
    def test_save_overlapping_timer(self):
        Timer.objects.create(
            worker=self.worker,
            start=NOW - timedelta(hours=2), end=NOW + timedelta(hours=2),
            kind=Timer.HOLIDAY)
        timer = Timer(
            worker=self.worker,
            start=NOW - timedelta(hours=1), end=NOW + timedelta(hours=5),
            kind=Timer.HOLIDAY)
        with self.assertRaises(ValidationError):
            timer.clean()

    def test_clean_for_negative_timer_fails(self):
        with self.assertRaises(ValidationError):
            timer = Timer(worker=self.worker, start=NOW, end=NOW - timedelta(days=2))
            timer.clean()


class TimerQuerySetTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()  # type: Company
        self.worker = UserFactory(company=self.company).access.first()
        self.worker2 = UserFactory(company=self.company).access.first()

    def test_filter_date(self):
        yesterday = timezone.now() - timedelta(days=1)
        Timer.objects.create(
            worker=self.worker,
            start=yesterday.replace(hour=9),
            end=yesterday.replace(hour=17)
        )
        timer = Timer.objects.create(
            worker=self.worker,
            duration=60 * 60 * 2
        )
        self.assertEqual(Timer.objects.filter_today().get(), timer)

    def test_filter_running(self):
        now = timezone.now().replace(hour=9)
        yesterday = now - timedelta(days=1)
        Timer.objects.create(
            worker=self.worker,
            start=yesterday,
            end=yesterday + timedelta(hours=8)
        )
        Timer.objects.create(
            worker=self.worker,
            duration=3600,
            kind=Timer.CORRECTION
        )
        self.assertFalse(Timer.objects.filter_running().exists())

        timer = Timer.launch(self.worker)
        self.assertEqual(
            Timer.objects.filter_running().get(),
            Timer.objects.get(pk=timer.pk)
        )

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
            worker=self.worker, start=start, end=end,
            kind=Timer.WORK, comment='Test comment'
        )
        result = Timer.objects.order_by('id').all()
        self.assertEqual(len(result), 9)  # 3 per day, two days skipped
        self.assertEqual(result[0].kind, Timer.WORK)
        self.assertEqual(result[0].comment, 'Test comment')
        self.assertEqual(result[0].start, start)  # left is UTC, right is CEST, automatically normalized for '=='
        self.assertEqual(result[0].start.hour, 5)  # different UTC from a CEST datetime
        self.assertEqual(result[6].start.hour, 6)  # different UTC from a CET datetime
        self.assertEqual(result[0].start.astimezone(tz).hour, 7)  # same local time
        self.assertEqual(result[6].start.astimezone(tz).hour, 7)  # same local time

    def test_stop_for_break(self):
        worker2 = UserFactory(company=self.company).access.first()
        with freeze_time('2016-08-16 07:00'):
            timer1 = Timer.launch(worker=self.worker)
            timer2 = Timer.launch(worker=worker2)
            outside_timer = Timer.objects.create(
                worker=self.worker,
                duration=3600,
                kind=Timer.CORRECTION,
                start=timezone.now() - timedelta(days=1)
            )

        with freeze_time('2016-08-16 09:00'):
            now = timezone.now()
            stopped_count = Timer.objects.stop_for_break()
            timer1.refresh_from_db()
            timer2.refresh_from_db()
            outside_timer.refresh_from_db()
            self.assertEqual(stopped_count, 2)
            self.assertEqual(timer1.end, now)
            self.assertEqual(timer2.end, now)
            self.assertTrue(timer1.is_auto_stopped)
            self.assertTrue(timer2.is_auto_stopped)
            self.assertEqual(outside_timer.end, outside_timer.start + timedelta(seconds=3600))

    def test_launch_after_break(self):
        worker2 = UserFactory(company=self.company).access.first()
        running_worker = UserFactory(company=self.company).access.first()
        manually_stopped_worker = UserFactory(company=self.company).access.first()
        with freeze_time('2016-08-16 07:00'):
            Timer.launch(worker=self.worker)
            Timer.launch(worker=worker2)
            manually_stopped_timer = Timer.launch(worker=manually_stopped_worker)

        with freeze_time('2016-08-16 09:00'):
            manually_stopped_timer.stop()
            Timer.objects.stop_for_break()

        with freeze_time('2016-08-16 09:15'):
            running_timer_started = timezone.now()
            Timer.launch(worker=running_worker)

        with freeze_time('2016-08-16 09:30'):
            Timer.objects.launch_after_break()
            now = timezone.now()
            timer1 = self.worker.timers.latest('start')
            timer2 = worker2.timers.latest('start')
            running_timer = running_worker.timers.latest('start')
            stopped_timer = manually_stopped_worker.timers.latest('start')
            self.assertEqual(timer1.start, now)
            self.assertEqual(timer2.start, now)
            self.assertTrue(timer1.is_auto_started)
            self.assertTrue(timer2.is_auto_started)
            self.assertEqual(running_timer.start, running_timer_started)
            self.assertTrue(running_timer.is_running)
            self.assertFalse(stopped_timer.is_running)

    # def test_stop_after_day