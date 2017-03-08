from datetime import timedelta, datetime

from django.test import TestCase
from django.utils import timezone

from ..company.models import Company, Worker
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from . import forms
from .models import Timer


class ManualTimerFormTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()  # type: Company
        self.worker = UserFactory(company=self.company).access.first()  # type: Worker

    def test_save(self):
        start = datetime(2016, 9, 1, 7, tzinfo=timezone.utc)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.strftime('%d.%m.%Y %H:%M'),
            'stopped': start.replace(hour=16).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.VACATION
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timer = form.save()[0]
        self.assertEqual(timer.duration, 60 * 9)

    def test_save_with_morning_break(self):
        start = datetime(2016, 9, 1, 7, tzinfo=timezone.utc)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.strftime('%d.%m.%Y %H:%M'),
            'stopped': start.replace(hour=16).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.WORK,
            'morning_break': True
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timer1, timer2 = form.save()
        self.assertEqual(timer1.duration, 60 * 2)
        self.assertEqual(timer2.duration, 60 * 6.5)

    def test_save_with_lunch_break(self):
        start = datetime(2016, 9, 1, 7, tzinfo=timezone.utc)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.strftime('%d.%m.%Y %H:%M'),
            'stopped': start.replace(hour=16).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.WORK,
            'lunch_break': True
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timer1, timer2 = form.save()
        self.assertEqual(timer1.duration, 60 * 5.5)
        self.assertEqual(timer2.duration, 60 * 3)

    def test_save_with_all_breaks(self):
        start = datetime(2016, 9, 1, 7, tzinfo=timezone.utc)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.strftime('%d.%m.%Y %H:%M'),
            'stopped': start.replace(hour=16).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.WORK,
            'morning_break': True,
            'lunch_break': True,
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timer1, timer2, timer3 = form.save()
        self.assertEqual(timer1.duration, 60 * 2)
        self.assertEqual(timer2.duration, 60 * 3)
        self.assertEqual(timer3.duration, 60 * 3)

    def test_save_days_span(self):
        """ This will test that the correct number of breaks were applied
            and weekends are not included (Sept 1 2016 is Thursday, we add 3 days,
            so one day should be skipped)."""
        start = datetime(2016, 9, 1, 7, tzinfo=timezone.utc)
        end = start + timedelta(days=3, hours=9)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.strftime('%d.%m.%Y %H:%M'),
            'stopped': end.strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.WORK,
            'morning_break': True,
            'lunch_break': True
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timers = form.save()
        self.assertEqual(len(timers), 6)  # 2 breaks per day, for 2 days

    def test_non_work_breaks_validation(self):
        start = datetime(2017, 1, 13, 7, tzinfo=timezone.utc)
        end = start + timedelta(days=5, hours=5)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.strftime('%d.%m.%Y %H:%M'),
            'stopped': end.strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.VACATION,
            'morning_break': True,
            'lunch_break': True
        }, company=self.company)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            ["Only work timers can have morning or lunch breaks."],
            form.non_field_errors()
        )

    def test_negative_timer_validation(self):
        start = datetime(2017, 1, 13, 10, tzinfo=timezone.utc)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.strftime('%d.%m.%Y %H:%M'),
            'stopped': start.replace(hour=7).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.WORK,
        }, company=self.company)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            ["Timer cannot be negative"],
            form.non_field_errors()
        )

    def test_overlap_validation(self):
        tz = timezone.get_default_timezone()
        start = tz.localize(datetime(2016, 9, 1, 7))
        Timer.start(self.worker, started=start, stopped=start.replace(hour=16))
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.strftime('%d.%m.%Y %H:%M'),
            'stopped': start.replace(hour=10).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.WORK
        }, company=self.company)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            ["Overlapping timer (01.09.2016 05:00 — 01.09.2016 14:00) already exists"],
            form.non_field_errors()
        )

    def test_additional_timer_without_overlap(self):
        tz = timezone.get_default_timezone()
        start = tz.localize(datetime(2016, 9, 1, 7))
        Timer.start(self.worker, started=start, stopped=start.replace(hour=16))
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'started': start.replace(hour=17).strftime('%d.%m.%Y %H:%M'),
            'stopped': start.replace(hour=19).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.WORK
        }, company=self.company)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Timer.objects.count(), 2)

    def test_worker_dropdown_label(self):
        f = forms.ManualTimerForm(company=self.company)
        self.assertEqual(
            self.worker.user.get_full_name(),
            list(f.fields['worker'].choices)[1][1])

