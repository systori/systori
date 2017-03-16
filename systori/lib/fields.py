from django import forms
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _


def apply_all_kwargs(obj, **kwargs):
    for field in obj._meta.get_fields():
        if field.attname in kwargs:
            value = kwargs.pop(field.attname)
            setattr(obj, field.attname, value)
    if kwargs:
        raise TypeError(
            "'{}' is not a valid field of {}"
            .format(list(kwargs)[0], obj.__class__.__name__)
        )


class RateType:
    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    FLAT = 'flat'
    RATE_CHOICES = [
        (HOURLY, _("Hourly")),
        (DAILY, _("Daily")),
        (WEEKLY, _("Weekly")),
        (FLAT, _("Flat Fee")),
    ]


class DecimalMinuteHoursField(forms.DecimalField):
    """
    This form field allows editing a minute based
    model field using an hour decimal conversion.
    Providing initial value of 60 will render
    1.0 in the input box, if user enters 1.5
    the cleaned value will be 90.
    """

    class BoundField(forms.BoundField):
        @cached_property
        def initial(self):
            data = self.form.get_initial_for_field(self.field, self.name)
            return data / 60.0

    def get_bound_field(self, form, field_name):
        return DecimalMinuteHoursField.BoundField(form, self, field_name)

    def clean(self, value):
        decimal = super().clean(value)
        return int(decimal * 60)
