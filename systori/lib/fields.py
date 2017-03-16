from django import forms
from django.utils.functional import cached_property


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
