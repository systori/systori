import unicodedata
from decimal import Decimal, DecimalException
from django.utils.encoding import smart_text
from django import forms
from django.conf import settings
from django.forms import ValidationError
from django.utils import formats, six


def sanitize_separators(value):
    """
    Sanitizes a value regardless the current decimal setting. 
    Used with form field input.
    """
    if isinstance(value, six.string_types):
        parts = []
        decimal_separator = formats.get_format('DECIMAL_SEPARATOR', use_l10n=True)
        if decimal_separator in value:
            value, decimals = value.split(decimal_separator, 1)
            parts.append(decimals)
        if settings.USE_THOUSAND_SEPARATOR:
            thousand_sep = formats.get_format('THOUSAND_SEPARATOR', use_l10n=True)
            if thousand_sep == '.' and value.count('.') == 1 and len(value.split('.')[-1]) != 3:
                # Special case where we suspect a dot meant decimal separator (see #22171)
                pass
            else:
                for replacement in {
                        thousand_sep, unicodedata.normalize('NFKD', thousand_sep)}:
                    value = value.replace(replacement, '')
        parts.append(value)
        value = '.'.join(reversed(parts))
    return value


class SmartDecimalField(forms.DecimalField):
    widget = forms.TextInput

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values. Ensures that there are no more
        than max_digits in the number, and no more than decimal_places digits
        after the decimal point.
        """
        if value in self.empty_values:
            return None
        if self.localize:
            value = sanitize_separators(value)
        value = smart_text(value).strip()
        try:
            value = Decimal(value)
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value
