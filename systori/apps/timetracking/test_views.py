import json
from datetime import timedelta

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

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
        self.assertTrue(Timer.objects.filter_running().filter(user=self.user).exists())

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


class ReportViewTest(TestCase):
    password = 'ReportViewTest'
    url = reverse('report')

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company, password=self.password)

    def test_get(self):
        now = timezone.now().replace(hour=18)
        yesterday = now - timedelta(days=1)
        timer1 = Timer.objects.create(
            user=self.user, 
            start=yesterday - timedelta(hours=10),
            end=yesterday - timedelta(hours=2)
        )
        timer2 = Timer.objects.create(
            user=self.user,
            start=yesterday - timedelta(hours=2),
            end=yesterday - timedelta(minutes=30)
        )
        timer3 = Timer.objects.create(
            user=self.user, 
            start=now - timedelta(hours=9),
            end=now - timedelta(hours=3)
        )
        timer4 = Timer.objects.create(
            user=self.user, 
            start=now - timedelta(hours=1),
            end=now - timedelta(minutes=30)
        )
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.get(self.url)
        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(json_response[0]['date'], now.strftime('%d %b %Y'))
        self.assertEqual(json_response[0]['start'], timer3.start.strftime('%H:%M'))
        self.assertEqual(json_response[0]['end'], timer4.end.strftime('%H:%M'))
        self.assertEqual(json_response[0]['total_duration'], '6:30')
        self.assertEqual(json_response[0]['total'], '5:30')
        self.assertEqual(json_response[0]['overtime'], '0:00')

        self.assertEqual(json_response[1]['date'], yesterday.strftime('%d %b %Y'))
        self.assertEqual(json_response[1]['start'], timer1.start.strftime('%H:%M'))
        self.assertEqual(json_response[1]['end'], timer2.end.strftime('%H:%M'))
        self.assertEqual(json_response[1]['total_duration'], '9:30')
        self.assertEqual(json_response[1]['total'], '8:30')
        self.assertEqual(json_response[1]['overtime'], '0:30')


    def test_get_empty(self, now=None):
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(json.loads(response.content.decode('utf-8')), [])
