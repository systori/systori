from unittest import TestCase
from django import forms
from .fields import DecimalMinuteHoursField


class SomeForm(forms.Form):
    minutes = DecimalMinuteHoursField(localize=True, initial=60)


class TestDecimalMinuteHoursField(TestCase):
    def test_initial(self):
        form = SomeForm()
        self.assertEqual(form["minutes"].initial, 1)
        self.assertEqual(form["minutes"].value(), 1)
        form = SomeForm(initial={"minutes": 90})
        self.assertEqual(form["minutes"].initial, 1.5)
        self.assertEqual(form["minutes"].value(), 1.5)

    def test_data(self):
        form = SomeForm(data={"minutes": "1.5"})
        form.full_clean()
        self.assertEqual(form.cleaned_data["minutes"], 90)
