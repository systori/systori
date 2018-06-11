from django import template
from ..utils import get_workers_statuses


register = template.Library()

USER_STATUSES = "_internal_variable_user_statuses"


@register.simple_tag(takes_context=True)
def load_user_statuses(context):
    context[USER_STATUSES] = get_workers_statuses()
    return ""


@register.inclusion_tag(
    filename="timetracking/user_status_snippet.html", takes_context=True
)
def show_user_status(context, worker):
    return {"worker": worker, "status": context[USER_STATUSES].get(worker.pk, None)}
