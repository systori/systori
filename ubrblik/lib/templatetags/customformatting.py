from django.template.defaultfilters import stringfilter
from django.utils.formats import get_format
from django import template
register = template.Library()

@register.filter
@stringfilter
def cleandecimal(decimal, max_decimal_places):
    """ 
    This filter attempts to normalize a decimal by either
    removing extra zeros past the max_decimal_places or
    by adding zeros up to max_decimal_places.
    This filter is intended to be called after floatformat (which adds thousands separators).
    """
    assert max_decimal_places > 0
    separator = get_format('DECIMAL_SEPARATOR')
    separator_pos = decimal.find(separator)
    if separator_pos == -1:
        decimal += separator
        separator_pos = len(decimal)

    significand = decimal[separator_pos+1:]
    if len(significand) > max_decimal_places:
        clean_significand = significand[:max_decimal_places] + significand[max_decimal_places:].rstrip('0')
        return decimal[:separator_pos+1] + clean_significand
    elif len(significand) < max_decimal_places:
        return decimal[:separator_pos+1] + significand.ljust(max_decimal_places, '0')
    else:
        return decimal