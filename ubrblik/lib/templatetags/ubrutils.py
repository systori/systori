from random import randint
from django import template
register = template.Library()

@register.simple_tag
def random_number(start, end):
    return randint(start, end)