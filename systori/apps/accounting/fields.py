from decimal import Decimal, DecimalException
import re
from django.utils import formats
from django.utils.encoding import smart_text
from django import forms
from django.forms import ValidationError


class SmartDecimalField(forms.DecimalField):
    widget = forms.TextInput

    def to_python(self, value):
        """
        Works like DecimalField but accepts all thousands and decimal separators
        or their combination.
        """
        if value in self.empty_values:
            return None
        value = re.sub(r'[\.\s,](?!\d{,2}$)', '', value)
        value = value.replace(',', '.')
        value = smart_text(value).strip()
        try:
            value = Decimal(value)
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value
