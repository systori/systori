from decimal import Decimal
from django import template
from django.utils.safestring import mark_safe

from .customformatting import ubrdecimal

register = template.Library()


def _make_context(context, css, obj, field, has_form=False):

    field_amount = field if field.endswith('_total') else field+'_amount'

    diff_field_amount = field_amount+'_diff'

    ctx = {
        'TAX_RATE': context['TAX_RATE'],
        'css_class': css,
        'amount': getattr(obj, field_amount),
        'diff': getattr(obj, diff_field_amount, None),
        'has_form': has_form
    }

    if has_form:
        ctx.update({
            'net': obj[field+'_net'],
            'tax': obj[field+'_tax'],
        })

    return ctx


@register.inclusion_tag('accounting/amount_view_cell.html', takes_context=True)
def amount_view(context, *args):
    return _make_context(context, *args)


@register.inclusion_tag('accounting/amount_view_cell.html', takes_context=True)
def amount_stateful(context, *args):
    return _make_context(context, *args, has_form=True)


@register.inclusion_tag('accounting/amount_input_cell.html', takes_context=True)
def amount_input(context, *args):
    return _make_context(context, *args, has_form=True)


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
