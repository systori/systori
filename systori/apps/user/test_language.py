from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import check_for_language, to_locale, get_language, LANGUAGE_SESSION_KEY

from systori.apps.project.models import Project
from .tests import CreateUserDataMixin


class CreateProjectMixin(CreateUserDataMixin):

    def setUp(self):
        super().setUp()
        Project.objects.create(name="Template Project", is_template=True)
        Project.objects.create(name="my project")


class SetLanguageViewTest(CreateProjectMixin, TestCase):

    def test_post(self):
        self.client.login(username=self.username, password=self.password)
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


class SetLanguageMiddlewareTest(CreateProjectMixin, TestCase):

    def test_process_request(self):
        self.assertIn(
            'systori.apps.user.middleware.SetLanguageMiddleware', 
            settings.MIDDLEWARE_CLASSES)
        self.client.login(username=self.username, password=self.password)

        self.user.language = 'en'
        self.user.save()
        response = self.client.get('/')
        self.assertEqual(response['Content-Language'], 'en')

        self.user.language = 'de'
        self.user.save()
        response = self.client.get('/')
        self.assertEqual(response['Content-Language'], 'de')
