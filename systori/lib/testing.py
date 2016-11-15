from django.test import TestCase
from rest_framework.test import APIClient
from django.conf import settings

from systori.apps.company.factories import CompanyFactory


class SubdomainClient(APIClient):
    """
    Enable Systori HTTP_HOST/subdomain functionality on test client requests
    """
    def generic(self, method, path, data='',
                content_type='application/octet-stream', secure=False,
                **extra):
        extra.setdefault('HTTP_HOST', CompanyFactory.schema + '.' + settings.SERVER_NAME)
        return super().generic(method, path, data, content_type, secure, **extra)


class SystoriTestCase(TestCase):
    client_class = SubdomainClient


def template_debug_output():
    """ Usage:

        try:
            self.client.get(...)
        except:
            template_debug_output()
    """
    import sys
    import html
    from django.views.debug import ExceptionReporter
    reporter = ExceptionReporter(None, *sys.exc_info())
    reporter.get_template_exception_info()
    info = reporter.template_info
    print()
    print('Exception Message: '+info['message'])
    print('Template: '+info['name'])
    print()
    for line in info['source_lines']:
        if line[0] == info['line']:
            print('-->'+html.unescape(line[1])[3:-1])
        else:
            print(html.unescape(line[1])[:-1])

