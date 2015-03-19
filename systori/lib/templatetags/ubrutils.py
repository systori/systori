from random import randint
from django import template
register = template.Library()

@register.simple_tag
def random_pick(*opts):
    return opts[randint(0, len(opts)-1)]