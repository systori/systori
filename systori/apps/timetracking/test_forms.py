import json
from datetime import timedelta

from django.test import TestCase
from django.forms import ValidationError
from django.utils import timezone

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
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)

    def test_save(self):
        now = timezone.now()
        form = forms.ManualTimerForm(data={
            'user': self.user.pk,
            'start': now.strftime('%d.%m.%Y %H:%M'),
            'end': (now + timedelta(hours=4)).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.HOLIDAY
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timer = form.save()
        self.assertEqual(timer.duration, 60 * 60 * 4)

    def test_save_days_span(self):
        now = timezone.now()
        # A hack to work around the fact that now is in UTC
        start = now.replace(hour=8 - 2, minute=0, second=0, microsecond=0)
        form = forms.ManualTimerForm(data={
            'user': self.user.pk,
            'start': now.strftime('%d.%m.%Y %H:%M'),
            'end': (now + timedelta(days=3)).strftime('%d.%m.%Y %H:%M'),
            'kind': Timer.HOLIDAY
        }, company=self.company)
        self.assertTrue(form.is_valid())
        timers = form.save()
        self.assertEqual(len(timers), 3)
        self.assertEqual(timers[0].start, start)
        self.assertEqual(
            timers[2].end,
            start + timedelta(days=2, seconds=Timer.WORK_HOURS)
        )
