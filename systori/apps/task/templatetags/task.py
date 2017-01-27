import re
from django import template
register = template.Library()


NUMBER = re.compile(r'^\s*[-+]?[0-9.,]*\s*$')


@register.filter
def is_formula(equation):

    if not isinstance(equation, str):
        return False

    if NUMBER.match(equation):
        return False

    return True
