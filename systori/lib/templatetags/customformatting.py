import locale
import math
from decimal import Decimal
from datetime import time, timedelta
from django.utils.formats import get_format, get_language, to_locale
from django.utils.translation import ungettext
from django import template

WORK_DAY = timedelta(hours=8).total_seconds()
HOLIDAYS_PER_MONTH = WORK_DAY * 2.5

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
def money(decimal):
    if decimal == '':
        return ''
    if type(decimal) is str:
        decimal = Decimal(decimal)
    locale.setlocale(locale.LC_ALL, (to_locale(get_language()), 'utf-8'))
    return locale.currency(decimal, True, True)


@register.filter
def todecimalhours(seconds):
    return ubrdecimal(seconds/60.0/60.0, max_significant=1, min_significant=0)


@register.filter
def hourslabel(seconds):
    return ungettext('hour', 'hours', seconds/60.0/60.0)


@register.filter
def hoursverbose(seconds):
    return '{} {}'.format(todecimalhours(seconds), hourslabel(seconds))


@register.filter
def toworkdays(seconds):
    return ubrdecimal(seconds/60.0/60.0/8.0, max_significant=1, min_significant=0)


@register.filter
def workdayslabel(seconds):
    return ungettext('day', 'days', seconds/60.0/60.0/8.0)


@register.filter
def workdaysverbose(seconds):
    return '{} {}'.format(toworkdays(seconds), workdayslabel(seconds))


@register.filter
def daysgained(seconds):
    return '{} - {}'.format(toworkdays(HOLIDAYS_PER_MONTH), workdaysverbose(seconds))


@register.filter
def hoursgained(seconds):
    return '{} - {}'.format(todecimalhours(HOLIDAYS_PER_MONTH), hoursverbose(seconds))


@register.filter
def dayshours(seconds):
    return '{} ({})'.format(workdaysverbose(seconds), hoursverbose(seconds))


@register.filter
def hoursdays(seconds):
    return '{} ({})'.format(hoursverbose(seconds), workdaysverbose(seconds))


@register.filter
def dayshoursgainedverbose(seconds):
    return '{} ({})'.format(daysgained(seconds), hoursgained(seconds))


@register.filter
def zeroblank(value):
    if value == '0': return ''
    return value


@register.filter
def tosexagesimalhours(seconds):
    mins, secs = divmod(abs(seconds), 60)
    if mins > 0:
        if secs >= 30:
            mins += 1
    hours, mins = divmod(mins, 60)
    return "{}{}:{:02}".format(
        '-' if seconds < 0 else '', hours, mins
    )

format_seconds = tosexagesimalhours
