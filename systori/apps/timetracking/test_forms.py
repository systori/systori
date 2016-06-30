import json
from datetime import timedelta

from django.test import TestCase
from django.forms import ValidationError

from . import forms


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
