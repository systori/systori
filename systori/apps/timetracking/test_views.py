import json
from datetime import datetime, timedelta

from urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework import status

from systori.lib.testing import SystoriTestCase
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer
from .utils import to_current_timezone as totz


class TimerViewTest(SystoriTestCase):
    password = 'TimerViewTest'
    url = reverse('timer')

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, password=self.password).access.first()
        self.client.login(username=self.worker.email, password=self.password)

    def test_post(self):
        response = self.client.post(self.url, {'start_latitude': '52.5076', 'start_longitude': '131.39043904'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Timer.objects.filter_running().filter(worker=self.worker).exists())

    def test_post_with_already_running_timer(self):
        Timer.launch(self.worker)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_post_without_coordinates(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_get(self):
        Timer.launch(self.worker)
        response = self.client.get(self.url)
        self.assertIn('duration', json.loads(response.content.decode('utf-8')))

    def test_get_no_timer(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_put_with_short_timer(self):
        timer = Timer.launch(self.worker)
        response = self.client.put(
            self.url,
            urlencode({'end_latitude': '52.5076', 'end_longitude': '131.39043904'}),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Timer.DoesNotExist):
            timer.refresh_from_db()

    def test_put(self):
        timer = Timer.objects.create(worker=self.worker, start=timezone.now() - timedelta(hours=1))
        response = self.client.put(
            self.url,
            urlencode({'end_latitude': '52.5076', 'end_longitude': '131.39043904'}),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200, response.data)
        timer.refresh_from_db()
        self.assertFalse(timer.is_running)


class ReportViewTest(SystoriTestCase):
    password = 'ReportViewTest'
    url = reverse('report')

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, password=self.password).access.first()

    def test_get(self):
        now = timezone.now().replace(hour=18, minute=0, second=0, microsecond=0)
        yesterday = now - timedelta(days=1)
        timer1 = Timer.objects.create(
            worker=self.worker,
            start=yesterday - timedelta(hours=10),
            end=yesterday - timedelta(hours=3)
        )
        timer2 = Timer.objects.create(
            worker=self.worker,
            start=yesterday - timedelta(hours=2),
            end=yesterday - timedelta(minutes=30)
        )
        timer3 = Timer.objects.create(
            worker=self.worker,
            start=now - timedelta(hours=9),
            end=now - timedelta(hours=3)
        )
        timer4 = Timer.objects.create(
            worker=self.worker,
            start=now - timedelta(hours=1),
            end=now - timedelta(minutes=30)
        )
        Timer.objects.create(
            worker=UserFactory(company=self.company).access.first(),
            start=now - timedelta(hours=1),
            end=now - timedelta(minutes=30)
        )

        self.client.login(username=self.worker.email, password=self.password)
        response = self.client.get(self.url)
        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(json_response[0]['date'], yesterday.strftime('%d.%m.%Y'))
        self.assertEqual(json_response[0]['start'], totz(timer1.start).strftime('%H:%M'))
        self.assertEqual(json_response[0]['end'], totz(timer1.end).strftime('%H:%M'))
        self.assertEqual(json_response[0]['duration'], '7:00')

        self.assertEqual(json_response[1]['date'], yesterday.strftime('%d.%m.%Y'))
        self.assertEqual(json_response[1]['start'], totz(timer2.start).strftime('%H:%M'))
        self.assertEqual(json_response[1]['end'], totz(timer2.end).strftime('%H:%M'))
        self.assertEqual(json_response[1]['duration'], '1:30')

        self.assertEqual(json_response[2]['date'], now.strftime('%d.%m.%Y'))
        self.assertEqual(json_response[2]['start'], totz(timer3.start).strftime('%H:%M'))
        self.assertEqual(json_response[2]['end'], totz(timer3.end).strftime('%H:%M'))
        self.assertEqual(json_response[2]['duration'], '6:00')

        self.assertEqual(json_response[3]['date'], now.strftime('%d.%m.%Y'))
        self.assertEqual(json_response[3]['start'], totz(timer4.start).strftime('%H:%M'))
        self.assertEqual(json_response[3]['end'], totz(timer4.end).strftime('%H:%M'))
        self.assertEqual(json_response[3]['duration'], '0:30')

    def test_get_empty(self):
        self.client.login(username=self.worker.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(json.loads(response.content.decode('utf-8')), [])


class UserReportViewTest(SystoriTestCase):
    password = 'UserReportViewTest'

    def setUp(self):
        self.another_company = CompanyFactory(schema='another_testcompany')
        self.another_worker = UserFactory(company=self.another_company, password=self.password).access.first()
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, password=self.password).access.first()

    def test_user_from_another_company_cannot_be_viewed(self):
        self.client.login(username=self.worker.email, password=self.password)
        response = self.client.get(reverse('timetracking_worker', args=[self.another_worker.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_from_current_company_can_be_viewed(self):
        self.client.login(username=self.worker.email, password=self.password)
        response = self.client.get(reverse('timetracking_worker', args=[self.worker.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
