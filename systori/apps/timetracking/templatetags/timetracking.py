from django import template
from django.contrib.auth import get_user_model

from .. import utils


register = template.Library()


@register.filter
def seconds_to_hours(value):
    return utils.format_seconds(value or 0)


class StatusLoader(template.Node):
    var_name = 'user_statuses'

    def render(self, context):
        context[self.var_name] = utils.get_users_statuses(get_user_model().objects.all())
        return ''


class StatusRenderer(template.Node):

    def __init__(self, user_variable):
        self.user_variable = template.Variable(user_variable)

    def render(self, context):
        try:
            user = self.user_variable.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        loaded_template = context.template.engine.get_template('timetracking/user_status_snippet.html')
        try:
            status = context[StatusLoader.var_name].get(user.pk, [None])[0]
        except KeyError:
            raise template.TemplateSyntaxError('Call {% load_user_statuses %} in the same template block')

        context = {
            'user': user, 'status': status
        }
        return loaded_template.render(template.context.Context(context))#, autoescape=context.autoescape))


@register.tag
def load_user_statuses(parser, token):
    return StatusLoader()


@register.tag
def show_user_status(parser, token):
    try:
        _, user_variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            '{} tag requires exactly one argument'.format(token.contents.split()[0])
        )
    return StatusRenderer(user_variable)
