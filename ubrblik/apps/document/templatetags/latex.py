from django.template.defaultfilters import stringfilter
from django import template
register = template.Library()

@register.filter
@stringfilter
def bold(value):
     return "\\textbf{{{}}}".format(value)
 