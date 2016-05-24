from django import template

from ..import utils


register = template.Library()


@register.filter
def seconds_to_hours(value):
    return utils.format_seconds(value or 0)
