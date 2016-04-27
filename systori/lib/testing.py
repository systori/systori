from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from tastypie.test import TestApiClient, ResourceTestCaseMixin

from systori.apps.company.factories import CompanyFactory


class SubdomainClient(Client):
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


class SubdomainApiClient(TestApiClient):

    def __init__(self):
        super().__init__()
        self.client = SubdomainClient()


class ApiTestCase(ResourceTestCaseMixin, SystoriTestCase):

    def setUp(self):
        super().setUp()
        self.api_client = SubdomainApiClient()

    def get_credentials(self):
        return self.create_basic('test@systori.com', 'open sesame')


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

