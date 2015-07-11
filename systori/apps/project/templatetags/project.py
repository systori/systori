from django import template
register = template.Library()


@register.assignment_tag(takes_context=True)
def project_phases(context):
    return context['project'].phases(context['access'])

@register.assignment_tag(takes_context=True)
def project_states(context):
    return context['project'].states(context['access'])