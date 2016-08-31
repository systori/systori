import json
from datetime import timedelta, datetime

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from freezegun import freeze_time

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer


NOW = timezone.now().replace(hour=12)


class TimerTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)

    def test_launch(self):
        timer = Timer.launch(self.user)
        self.assertTrue(timer.pk)
        self.assertEqual(timer.user, self.user)
        self.assertTrue(timer.is_running)

    def test_launch_with_kwargs(self):
        timer = Timer.launch(self.user, start_latitude=52.5076, start_longitude=13.3904)
        self.assertTrue(timer.pk)
        self.assertEqual(timer.user, self.user)
        self.assertEqual(timer.start_latitude, 52.5076)
        self.assertEqual(timer.start_longitude, 13.3904)
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
        timer.stop(ignore_short_duration=False)
        self.assertTrue(timer.end)

    @freeze_time('2016-08-16 18:30')
    def test_stop_with_supplied_timestamp(self):
        timer = Timer.launch(self.user)
        timer.stop(end=timezone.now() + timedelta(hours=2))
        self.assertEqual(timer.end.strftime('%H:%M'), '20:30')

    def test_stop_with_extra_params(self):
        with freeze_time(timezone.now() - timedelta(hours=3)):
            timer = Timer.launch(self.user)
        timer.stop(is_auto_stopped=True, comment='test comment')
        timer.refresh_from_db()
        self.assertTrue(timer.is_auto_stopped)
        self.assertEqual(timer.comment, 'test comment')

    def test_stop_zero_timer_ignores_it(self):
        timer = Timer.launch(self.user)
        timer.stop()
        self.assertFalse(Timer.objects.filter(pk=timer.pk).exists())

    def test_to_dict(self):
        timer = Timer.launch(self.user)
        self.assertEqual(
            timer.to_dict(),
            {'duration': timer.get_duration()}
        )

    @freeze_time(NOW)
    def test_save_regular_timer(self):
        # Regular timer
        timer = Timer(user=self.user)
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertIsNone(timer.end)

        with self.assertRaises(ValidationError):
            timer = Timer(user=self.user)
            timer.clean()

    @freeze_time(NOW)
    def test_save_with_end(self):
        timer = Timer(user=self.user, end=NOW + timedelta(hours=2))
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertEqual(timer.duration, 60 * 60 * 2)

    @freeze_time(NOW)
    def test_save_with_duration(self):
        timer = Timer(user=self.user, duration=60 * 60 * 2)
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertEqual(timer.end, NOW + timedelta(hours=2))

    @freeze_time(NOW)
    def test_save_correction_timer(self):
        timer = Timer(user=self.user, duration=60 * 60 * 2, kind=Timer.CORRECTION)
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.end, NOW + timedelta(hours=2))
        self.assertEqual(timer.date, NOW.date())

    @freeze_time(NOW)
    def test_save_overlapping_timer(self):
        Timer.objects.create(
            user=self.user,
            start=NOW - timedelta(hours=2), end=NOW + timedelta(hours=2),
            kind=Timer.HOLIDAY)
        timer = Timer(
            user=self.user,
            start=NOW - timedelta(hours=1), end=NOW + timedelta(hours=5),
            kind=Timer.HOLIDAY)
        with self.assertRaises(ValidationError):
            timer.clean()

    def test_clean_for_negative_timer_fails(self):
        with self.assertRaises(ValidationError):
            timer = Timer(user=self.user, start=NOW, end=NOW - timedelta(days=2))
            timer.clean()

    def test_clean_for_long_timer_fails(self):
        with self.assertRaises(ValidationError):
            timer = Timer(user=self.user, start=NOW, end=NOW + timedelta(days=2))
            timer.clean()


class TimerQuerySetTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.user2 = UserFactory(company=self.company)

    def test_filter_date(self):
        now = timezone.now().replace(hour=9)
        yesterday = now - timedelta(days=1)
        Timer.objects.create(
            user=self.user,
            start=yesterday,
            end=yesterday + timedelta(hours=8)
        )

        timer = Timer(user=self.user, duration=60 * 60 * 2)
        timer.save()
        self.assertEqual(
            Timer.objects.filter_date().get(),
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
        Timer.objects.create(
            user=self.user,
            duration=3600,
            kind=Timer.CORRECTION
        )
        self.assertFalse(Timer.objects.filter_running().exists())

        timer = Timer.launch(self.user)
        self.assertEqual(
            Timer.objects.filter_running().get(),
            Timer.objects.get(pk=timer.pk)
        )

    def test_create_batch(self):
        now = timezone.now()
        start = now.replace(hour=7, minute=0, second=0, microsecond=0)
        result = Timer.objects.create_batch(
            user=self.user, days=3, start=now,
            kind=Timer.HOLIDAY, comment='Test comment'
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].start, start)
        self.assertEqual(result[0].end, start + timedelta(seconds=Timer.WORK_HOURS))
        self.assertEqual(result[0].kind, Timer.HOLIDAY)
        self.assertEqual(result[0].comment, 'Test comment')
        self.assertEqual(result[1].start, start + timedelta(days=1))
        self.assertEqual(result[1].end, start + timedelta(days=1) + timedelta(seconds=Timer.WORK_HOURS))
        self.assertEqual(result[2].start, start + timedelta(days=2))
        self.assertEqual(result[2].end, start + timedelta(days=2) + timedelta(seconds=Timer.WORK_HOURS))

    def test_stop_for_break(self):
        user2 = UserFactory(company=self.company)
        with freeze_time('2016-08-16 07:00'):
            timer1 = Timer.launch(user=self.user)
            timer2 = Timer.launch(user=user2)
            outside_timer = Timer.objects.create(
                user=self.user,
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
        user2 = UserFactory(company=self.company)
        running_user = UserFactory(company=self.company)
        manually_stopped_user = UserFactory(company=self.company)
        with freeze_time('2016-08-16 07:00'):
            Timer.launch(user=self.user)
            Timer.launch(user=user2)
            manually_stopped_timer = Timer.launch(user=manually_stopped_user)

        with freeze_time('2016-08-16 09:00'):
            manually_stopped_timer.stop()
            Timer.objects.stop_for_break()

        with freeze_time('2016-08-16 09:15'):
            running_timer_started = timezone.now()
            Timer.launch(user=running_user)

        with freeze_time('2016-08-16 09:30'):
            Timer.objects.launch_after_break()
            now = timezone.now()
            timer1 = self.user.timer_set.latest('start')
            timer2 = user2.timer_set.latest('start')
            running_timer = running_user.timer_set.latest('start')
            stopped_timer = manually_stopped_user.timer_set.latest('start')
            self.assertEqual(timer1.start, now)
            self.assertEqual(timer2.start, now)
            self.assertTrue(timer1.is_auto_started)
            self.assertTrue(timer2.is_auto_started)
            self.assertEqual(running_timer.start, running_timer_started)
            self.assertTrue(running_timer.is_running)
            self.assertFalse(stopped_timer.is_running)

    # def test_stop_after_day