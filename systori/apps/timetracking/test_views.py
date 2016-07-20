import json
from datetime import timedelta

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.utils import timezone

from systori.lib.testing import SystoriTestCase
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer


class TimerViewTest(SystoriTestCase):
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
        with self.assertRaises(Timer.DoesNotExist):
            timer.refresh_from_db()

    def test_put(self):
        timer = Timer.objects.create(user=self.user, start=timezone.now() - timedelta(hours=1))
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 200)
        timer.refresh_from_db()
        self.assertFalse(timer.is_running)


@override_settings(TIME_ZONE='Etc/UTC')
class ReportViewTest(SystoriTestCase):
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
            end=yesterday - timedelta(hours=3)
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
        Timer.objects.create(
            user=UserFactory(company=self.company),
            start=now - timedelta(hours=1),
            end=now - timedelta(minutes=30)
        )

        self.client.login(username=self.user.email, password=self.password)
        response = self.client.get(self.url)
        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(json_response[0]['date'], yesterday.strftime('%d.%m.%Y'))
        self.assertEqual(json_response[0]['start'], timer1.start.strftime('%H:%M'))
        self.assertEqual(json_response[0]['end'], timer1.end.strftime('%H:%M'))
        self.assertEqual(json_response[0]['duration'], '7:00')

        self.assertEqual(json_response[1]['date'], yesterday.strftime('%d.%m.%Y'))
        self.assertEqual(json_response[1]['start'], timer2.start.strftime('%H:%M'))
        self.assertEqual(json_response[1]['end'], timer2.end.strftime('%H:%M'))
        self.assertEqual(json_response[1]['duration'], '1:30')

        self.assertEqual(json_response[2]['date'], now.strftime('%d.%m.%Y'))
        self.assertEqual(json_response[2]['start'], timer3.start.strftime('%H:%M'))
        self.assertEqual(json_response[2]['end'], timer3.end.strftime('%H:%M'))
        self.assertEqual(json_response[2]['duration'], '6:00')

        self.assertEqual(json_response[3]['date'], now.strftime('%d.%m.%Y'))
        self.assertEqual(json_response[3]['start'], timer4.start.strftime('%H:%M'))
        self.assertEqual(json_response[3]['end'], timer4.end.strftime('%H:%M'))
        self.assertEqual(json_response[3]['duration'], '0:30')

    def test_get_empty(self, now=None):
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(json.loads(response.content.decode('utf-8')), [])
