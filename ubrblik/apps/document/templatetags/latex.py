from django.template.defaultfilters import stringfilter
from django import template
import re
register = template.Library()

@register.filter
@stringfilter
def bold(text):
    """
        :param text: a plain text message
        :return: the message returned to appear with Bold text styling in LaTeX
    """
    return "\\bfseries{{{}}}".format(text)

@register.filter
@stringfilter
def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless',
        '>': r'\textgreater',
        '\r':r'\hfill\\',
    }
    conv = dict((re.escape(k), v) for k, v in conv.items())
    pattern = re.compile("|".join(conv.keys()))
    return pattern.sub(lambda m: conv[re.escape(m.group(0))], text)

@register.filter
@stringfilter
def trim(value):
        return value.strip()
