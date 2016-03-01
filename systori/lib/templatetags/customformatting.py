import locale
import calendar
from decimal import Decimal
from django.utils.safestring import mark_safe
from django.utils.formats import get_format, get_language, number_format, to_locale
from django import template

register = template.Library()


@register.filter
def ubrdecimal(decimal, decimal_pos=4):
    if decimal == '': return ''

    if type(decimal) is str:
        decimal = Decimal(decimal)

    decimal = round(decimal, decimal_pos)

    decimal = number_format(decimal, decimal_pos=decimal_pos, use_l10n=True, force_grouping=True)

    separator = get_format('DECIMAL_SEPARATOR', use_l10n=True)
    separator_pos = decimal.find(separator)
    if separator_pos == -1:
        decimal += separator
        separator_pos = len(decimal)

    min_decimal_places = 2
    significand = decimal[separator_pos + 1:]
    if len(significand) > min_decimal_places:
        clean_significand = significand[:min_decimal_places] + significand[min_decimal_places:].rstrip('0')
        return decimal[:separator_pos + 1] + clean_significand
    elif len(significand) < min_decimal_places:
        return decimal[:separator_pos + 1] + significand.ljust(min_decimal_places, '0')
    else:
        return decimal


@register.filter
def money(decimal):
    if type(decimal) is str: decimal = Decimal(decimal)
    locale.setlocale(locale.LC_ALL, (to_locale(get_language()), 'utf-8'))
    return locale.currency(decimal, True, True)


@register.filter
def negate(value):
    return -value


@register.filter
def color_pos_neg(value):
    if value == 0:
        return ''
    elif value > 0:
        color = 'green'
    else:
        color = 'red'
    return mark_safe('<span style="color: %s;">%s</span>' % (color, ubrdecimal(value, 2)))


@register.filter
def month_from_int(value):
    return calendar.month_name[value]