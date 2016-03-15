import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer


class TimerViewTest(TestCase):
    password = 'TimerViewTest'
    url = reverse('timer')

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company, password=self.password)

    def test_post(self):
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Timer.objects.get_running().filter(user=self.user).exists())

    def test_post_error(self):
        timer = Timer.launch(self.user)
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_get(self):
        Timer.launch(self.user)
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.get(self.url)
        self.assertIn('duration', json.loads(response.content.decode('utf-8')))

    def test_get_no_timer(self, now=None):
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_put(self):
        timer = Timer.launch(self.user)
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 200)
        timer.refresh_from_db()
        self.assertFalse(timer.is_running)
