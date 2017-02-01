from django.conf import settings
from django.urls import reverse

from systori.lib.testing import SystoriTestCase
from systori.apps.company.factories import CompanyFactory
from systori.apps.user.factories import UserFactory


class LanguageTestCase(SystoriTestCase):

    def setUp(self):
        super().setUp()
        self.user = UserFactory(company=CompanyFactory())
        self.client.login(username=self.user.email, password='open sesame')


class SetLanguageViewTest(LanguageTestCase):

    def test_post(self):
        set_language_url = reverse('set_language')

        self.client.post(set_language_url, {'language': 'de'})
        response = self.client.get('/')
        self.assertEqual(response['Content-Language'], 'de')
        user = type(self.user).objects.get(pk=self.user.pk)
        self.assertEqual(user.language, 'de')

        self.client.post(set_language_url, {'language': 'en'})
        response = self.client.get('/')
        self.assertEqual(response['Content-Language'], 'en')
        user = type(self.user).objects.get(pk=self.user.pk)
        self.assertEqual(user.language, 'en')

        self.client.post(set_language_url, {'language': 'WRONG'})
        response = self.client.get('/')
        self.assertEqual(response['Content-Language'], 'en')
        user = type(self.user).objects.get(pk=self.user.pk)
        self.assertEqual(user.language, 'en')


class SetLanguageMiddlewareTest(LanguageTestCase):

    def test_process_request(self):
        self.assertIn(
            'systori.apps.user.middleware.SetLanguageMiddleware', 
            settings.MIDDLEWARE_CLASSES)

        self.user.language = 'en'
        self.user.save()
        response = self.client.get('/')
        self.assertEqual(response['Content-Language'], 'en')

        self.user.language = 'de'
        self.user.save()
        response = self.client.get('/')
        self.assertEqual(response['Content-Language'], 'de')
