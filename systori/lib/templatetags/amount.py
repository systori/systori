from decimal import Decimal
from django import template
from django.utils.safestring import mark_safe

from .customformatting import ubrdecimal

register = template.Library()


def _make_context(context, css, obj, field, bold="gross", has_form=False, select_if_equal=None):

    ctx = {
        'TAX_RATE': context['TAX_RATE'],
        'css_class': css,
        'amount': getattr(obj, field+'_amount'),
        'diff': getattr(obj, field+'_diff_amount', None),
        'percent': getattr(obj, field+'_percent', None),
        'has_form': has_form,
        'bold': bold
    }

    if select_if_equal == ctx['amount']:
        ctx['css_class'] += ' selected'

    if has_form:
        ctx.update({
            'net': obj[field+'_net'],
            'tax': obj[field+'_tax'],
        })

    return ctx


@register.inclusion_tag('accounting/amount_view_cell.html', takes_context=True)
def amount_view(context, *args, **kwargs):
    return _make_context(context, *args, **kwargs)


@register.inclusion_tag('accounting/amount_view_cell.html', takes_context=True)
def amount_stateful(context, *args, **kwargs):
    return _make_context(context, *args, has_form=True, **kwargs)


@register.inclusion_tag('accounting/amount_input_cell.html', takes_context=True)
def amount_input(context, *args, **kwargs):
    return _make_context(context, *args, has_form=True, **kwargs)


@register.simple_tag
def amount_diff_part(amount, part):
    color = ''
    value = getattr(amount, part, Decimal(0))
    if value > 0:
        color = 'green'
    elif value < 0:
        color = 'red'
    str_value = ''
    if value != 0:
        str_value = ubrdecimal(value, 2)
    if value > 0:
        str_value = '+'+str_value
    return mark_safe('<span class="amount-diff %s">%s</span>' % (color, str_value))


@register.simple_tag
def amount_value_part(amount, part):
    value = getattr(amount, part, Decimal(0))
    str_value = ubrdecimal(value, 2)
    return mark_safe('<span class="amount-value">%s</span>' % (str_value,))


@register.simple_tag
def amount_percent(percent):
    color = ''
    str_value = ''
    if percent is not None:
        str_value = str(percent)+'%'
        if percent == 100:
            color = 'green'
        elif percent > 100:
            color = 'red'
        elif percent < 100:
            color = 'blue'
    return mark_safe('<div class="amount-percent %s">%s</div>' % (color, str_value))
