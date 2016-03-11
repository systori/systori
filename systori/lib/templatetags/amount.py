from django import template

register = template.Library()


@register.inclusion_tag('accounting/amount_view_cell.html', takes_context=True)
def amount_view(context, css, obj, field):
    return {
        'TAX_RATE': context['TAX_RATE'],
        'css_class': css,
        'amount': getattr(obj, field+'_amount'),
        'has_form': False
    }


@register.inclusion_tag('accounting/amount_view_cell.html', takes_context=True)
def amount_view_input(context, css, obj, field):
    return {
        'TAX_RATE': context['TAX_RATE'],
        'css_class': css,
        'amount': getattr(obj, field+'_amount'),
        'has_form': True,
        'net': obj[field+'_net'],
        'tax': obj[field+'_tax'],
        'gross': obj[field+'_gross']
    }


@register.inclusion_tag('accounting/amount_input_cell.html', takes_context=True)
def amount_input(context, css, obj, field):
    return {
        'TAX_RATE': context['TAX_RATE'],
        'css_class': css,
        'amount': getattr(obj, field+'_amount'),
        'net': obj[field+'_net'],
        'tax': obj[field+'_tax'],
        'gross': obj[field+'_gross']
    }
