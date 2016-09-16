import json
from datetime import timedelta, datetime

from django.test import TestCase
from django.forms import ValidationError
from django.utils import timezone

from ..company.models import Company, Worker
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from . import forms
from .models import Timer


class DurationFieldTest(TestCase):

    def test_field(self):
        field = forms.DurationField('garbage')
        with self.assertRaises(ValidationError):
            field.clean('garbage')
        self.assertEqual(int(60 * 60 * 1.5), field.clean('1h 30m'))
        self.assertEqual(int(60 * 60 * 0.5), field.clean('30m'))
        self.assertEqual(60 * 60, field.clean('1h'))
        self.assertEqual(int(60 * 60 * -1.5), field.clean('-1h 30m'))
        self.assertEqual(int(60 * 60 * -0.5), field.clean('-30m'))
        self.assertEqual(60 * 60 * -1, field.clean('-1h'))


class ManualTimerFormTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()  # type: Company
        self.worker = UserFactory(company=self.company).access.first()

    def test_save(self):
        tz = timezone.get_current_timezone()
        start = tz.localize(datetime(2016, 9, 1, 7))
        end = start + timedelta(hours=9)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'start': start.strftime('%d.%m.%Y %H:%M'),
            'end': end.strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.HOLIDAY
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timer = form.save()[0]
        self.assertEqual(timer.duration, 60 * 60 * 2)

    def test_save_days_span(self):
        """ This will test that the correct number of breaks were applied
            and weekends are not included (Sept 1 2016 is Thursday, we add 3 days,
            so one day should be skipped)."""
        tz = timezone.get_current_timezone()
        start = tz.localize(datetime(2016, 9, 1, 7))
        end = start + timedelta(days=3, hours=9)
        form = forms.ManualTimerForm(data={
            'worker': self.worker.pk,
            'start': start.strftime('%d.%m.%Y %H:%M'),
            'end': end.strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.WORK
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timers = form.save()
        self.assertEqual(len(timers), 6)  # 3 breaks per day, for 2 days

    def test_worker_dropdown_label(self):
        f = forms.ManualTimerForm(company=self.company)
        self.assertEqual(
            self.worker.user.get_full_name(),
            list(f.fields['worker'].choices)[1][1])
