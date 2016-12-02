from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient
from django.conf import settings

from systori.apps.accounting.constants import TAX_RATE
from systori.apps.company.factories import CompanyFactory
from systori.apps.user.factories import UserFactory

from .accounting.tools import Amount


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


class ClientTestCase(SystoriTestCase):
    password = 'open sesame'

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company, language='en', password=self.password)
        self.worker = self.user.access.first()
        self.client.login(username=self.worker.email, password=self.password)


def make_amount(g=None, n=None, t=None):
    if g and n == 0 and t == 0:
        return Amount(Decimal(0), Decimal(0), Decimal(g))
    if g:
        return Amount.from_gross(Decimal(g), TAX_RATE)
    if n and not t:
        return Amount(Decimal(n), Decimal(0))
    if not n and t:
        return Amount(Decimal(0), Decimal(t))
    if n and t:
        return Amount(Decimal(n), Decimal(t))
    return Amount.zero()


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

