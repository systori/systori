import re
from django import template
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from systori.apps.task.views import JobCopy

register = template.Library()


NUMBER = re.compile(r"^\s*[-+]?[0-9.,]*\s*$")


@register.filter
def is_formula(equation):

    if not isinstance(equation, str):
        return False

    if NUMBER.match(equation):
        return False

    return True


@register.simple_tag(takes_context=True)
def paste_job(context):
    if JobCopy.SESSION_KEY in context["request"].session:
        return format_html(
            '<a href="{}" class="btn btn-success">{} #{}</a>',
            reverse("job.paste", args=[context["project"].id]),
            _("Paste Job"),
            context["request"].session[JobCopy.SESSION_KEY],
        )
    return ""
