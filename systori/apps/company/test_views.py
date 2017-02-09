from django.urls import reverse
from django.conf import settings

from systori.lib.testing import ClientTestCase
from .factories import CompanyFactory, WorkerFactory


class TestCompanyListView(ClientTestCase):

    def test_company_middleware_redirects_on_one_company(self):
        response = self.client.get(reverse('home'), HTTP_HOST=settings.SERVER_NAME)
        self.assertRedirects(response, 'http://' + CompanyFactory.schema + '.' + settings.SERVER_NAME)

    def test_company_list(self):
        WorkerFactory(user=self.user, company=CompanyFactory(schema='testschema2'))
        response = self.client.get(reverse('companies'), HTTP_HOST=settings.SERVER_NAME)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'testcompany')
        self.assertContains(response, 'testschema2')
