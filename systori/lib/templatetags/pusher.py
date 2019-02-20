import os
from django import template


register = template.Library()


@register.simple_tag
def pusher_key():
    return os.environ.get("PUSHER_KEY", "")
