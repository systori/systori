import locale
import math
from decimal import Decimal
from django.utils.formats import get_format, get_language, to_locale
from django.utils.translation import ugettext_lazy as _
from django import template

register = template.Library()


@register.filter('sum')
def _sum(data):
    return sum(data)


@register.filter
def lookup(key, data):
    return data[key]


@register.filter
def split_rows_vertically(data, cols):
    if not data: return data
    data = list(data)
    max_rows = math.ceil(len(data)/cols) if len(data) > cols else 1
    rows = []
    for rowIdx in range(max_rows):
        row = []
        for colIdx in range(cols):
            dataIdx = rowIdx + colIdx*max_rows
            row.append(data[dataIdx] if dataIdx < len(data) else '')
        rows.append(row)
    return rows


@register.filter
def split_rows_horizontally(data, cols):
    data = list(data)
    max_rows = int(len(data)/cols) + len(data) % cols
    rows = []
    for rowIdx in range(max_rows):
        row = []
        for colIdx in range(cols):
            dataIdx = (rowIdx*cols) + colIdx
            row.append(data[dataIdx] if dataIdx < len(data) else '')
        rows.append(row)
    return rows


@register.simple_tag
def company_url(company, request):
    return company.url(request)


@register.filter
def ubrdecimal(number, max_significant=4, min_significant=2):

    if number == '':
        return ''

    if type(number) is str:
        number = Decimal(number)

    number = round(number, max_significant)

    lang = get_language()
    radix = get_format('DECIMAL_SEPARATOR', lang, use_l10n=True)
    grouping = get_format('NUMBER_GROUPING', lang, use_l10n=True)
    thousand_sep = get_format('THOUSAND_SEPARATOR', lang, use_l10n=True)

    # sign
    sign = ''
    str_number = '{:f}'.format(number)
    if str_number[0] == '-':
        sign = '-'
        str_number = str_number[1:]

    # decimal part
    if '.' in str_number:
        int_part, dec_part = str_number.split('.')
        dec_part = dec_part.rstrip('0').ljust(min_significant, '0')
    else:
        int_part, dec_part = str_number, ''

    if dec_part:
        dec_part = radix + dec_part

    # grouping
    int_part_gd = ''
    for cnt, digit in enumerate(int_part[::-1]):
        if cnt and not cnt % grouping:
            int_part_gd += thousand_sep[::-1]
        int_part_gd += digit
    int_part = int_part_gd[::-1]

    return sign + int_part + dec_part


@register.filter
def ubrnumber(number):
    return ubrdecimal(number, min_significant=0)


@register.filter
def ubrhour(seconds):
    return ubrdecimal(seconds/60.0/60.0, max_significant=1, min_significant=0)


@register.filter
def ubrhourdays(seconds):
    return '{} {}'.format(
        ubrdecimal(seconds/60.0/60.0/8.0, max_significant=2, min_significant=0),
        _('days')
    )


@register.filter
def money(decimal):
    if decimal == '':
        return ''
    if type(decimal) is str:
        decimal = Decimal(decimal)
    locale.setlocale(locale.LC_ALL, (to_locale(get_language()), 'utf-8'))
    return locale.currency(decimal, True, True)
