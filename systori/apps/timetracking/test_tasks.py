from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer
from . import tasks


class TasksTest(TestCase):
    @freeze_time("2016-08-16 1:00")
    def test_start_or_stop_work_breaks(self):
        company1 = CompanyFactory(schema="berlin", timezone="Europe/Berlin")
        worker1 = UserFactory(company=company1).access.first()
        berlin = timezone.localtime()  # CEST +2 DST
        timer1 = Timer.objects.create(worker=worker1, started=berlin.replace(hour=7))
        previous1 = None

        company2 = CompanyFactory(schema="kiev", timezone="Europe/Kiev")
        worker2 = UserFactory(company=company2).access.first()
        kiev = timezone.localtime()  # EEST +3 DST
        timer2 = Timer.objects.create(worker=worker2, started=kiev.replace(hour=7))
        previous2 = None

        def run():
            nonlocal timer1, previous1, timer2, previous2
            tasks.start_or_stop_work_breaks()
            company1.activate()
            timer1 = worker1.timers.latest("started")
            previous1 = (
                worker1.timers.filter(stopped__isnull=False).order_by("stopped").first()
            )
            company2.activate()
            timer2 = worker2.timers.latest("started")
            previous2 = (
                worker2.timers.filter(stopped__isnull=False).order_by("stopped").first()
            )

        with freeze_time(berlin.replace(hour=8)):
            run()
            self.assertTrue(timer1.is_running)  # Berlin still running, it's 8am
            self.assertIsNone(previous1)
            self.assertFalse(timer2.is_running)  # Kiev stopped, it's 9am
            self.assertEqual(timer2, previous2)  # one stopped timer

        with freeze_time(berlin.replace(hour=8, minute=30)):
            run()
            self.assertTrue(timer1.is_running)  # Berlin still running, it's 8:30am
            self.assertIsNone(previous1)
            self.assertTrue(timer2.is_running)  # Kiev started new timer, it's 9:30am
            self.assertEqual(previous2.started.hour, 4)  # old timer (UTC)
            self.assertEqual(timer2.started.hour, 6)  # new timer (UTC)

        with freeze_time(berlin.replace(hour=9)):
            run()
            self.assertFalse(timer1.is_running)  # Berlin stopped, it's 9am
            self.assertEqual(timer1, previous1)  # one stopped timer
            self.assertTrue(timer2.is_running)  # Kiev still running, it's 10am

        with freeze_time(berlin.replace(hour=9, minute=30)):
            run()
            self.assertTrue(timer1.is_running)  # Berlin started new timer, it's 9:30am
            self.assertEqual(previous1.started.hour, 5)  # old timer (UTC)
            self.assertEqual(timer1.started.hour, 7)  # new timer (UTC)
            self.assertTrue(timer2.is_running)  # Kiev still running, it's 10:30am

    @freeze_time("2016-08-16 18:30")
    def test_stop_abandoned_timers(self):
        company1 = CompanyFactory()
        worker1 = UserFactory(company=company1).access.first()
        Timer.objects.create(
            worker=worker1, started=timezone.now() - timedelta(hours=7)
        )

        company2 = CompanyFactory(schema="testcompany2")
        worker2 = UserFactory(company=company2).access.first()
        Timer.objects.create(
            worker=worker2, started=timezone.now() - timedelta(hours=5)
        )

        company1.activate()
        self.assertTrue(Timer.objects.running().exists())
        company2.activate()
        self.assertTrue(Timer.objects.running().exists())

        tasks.stop_abandoned_timers()

        company1.activate()
        self.assertFalse(Timer.objects.running().exists())
        company2.activate()
        self.assertFalse(Timer.objects.running().exists())
