import locale
from django.template.defaultfilters import stringfilter
from django.utils.formats import get_format, get_language, number_format
from django import template
register = template.Library()

@register.filter
def ubrdecimal(decimal, decimal_pos=4):

    if decimal == '': return ''

    decimal = round(decimal, decimal_pos)

    decimal = number_format(decimal, decimal_pos=decimal_pos, use_l10n=True, force_grouping=True)

    separator = get_format('DECIMAL_SEPARATOR', use_l10n=True)
    separator_pos = decimal.find(separator)
    if separator_pos == -1:
        decimal += separator
        separator_pos = len(decimal)

    min_decimal_places = 2
    significand = decimal[separator_pos+1:]
    if len(significand) > min_decimal_places:
        clean_significand = significand[:min_decimal_places] + significand[min_decimal_places:].rstrip('0')
        return decimal[:separator_pos+1] + clean_significand
    elif len(significand) < min_decimal_places:
        return decimal[:separator_pos+1] + significand.ljust(min_decimal_places, '0')
    else:
        return decimal

@register.filter
def money(decimal):
    locale.setlocale(locale.LC_ALL, (get_language(), 'utf-8'))
    return locale.currency(decimal, True, True)
