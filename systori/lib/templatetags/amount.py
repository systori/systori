from django import template

register = template.Library()


def _make_context(context, css, obj, field, has_form=False):

    field_amount = field if field.endswith('_total') else field+'_amount'

    ctx = {
        'TAX_RATE': context['TAX_RATE'],
        'css_class': css,
        'amount': getattr(obj, field_amount),
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
