from django.test import TestCase
from django.test.client import Client
from django.conf import settings

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
