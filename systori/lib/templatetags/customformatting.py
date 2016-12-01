import locale
from decimal import Decimal
from django.utils.formats import get_format, get_language, to_locale
from django import template

register = template.Library()


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
