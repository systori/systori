from django.urls import reverse

from systori.lib.testing import ClientTestCase

from .workflow import create_chart_of_accounts


class AccountingViewTests(ClientTestCase):
    def test_accounts_list(self):
        create_chart_of_accounts()
        response = self.client.get(reverse("accounts"))
        self.assertEqual(200, response.status_code)
