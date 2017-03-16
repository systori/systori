from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from systori.lib.testing import ClientTestCase
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer


class UserReportViewTest(ClientTestCase):
    password = 'UserReportViewTest'

    def test_default_case(self):
        response = self.client.get(reverse('timetracking_worker', args=[self.worker.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['report_period'].month, datetime.now().month)
        self.assertEqual(response.context['report_period'].year, datetime.now().year)

    def test_user_from_another_company_cannot_be_viewed(self):
        another_company = CompanyFactory(schema='another_testcompany')
        another_worker = UserFactory(company=another_company, password=self.password).access.first()
        response = self.client.get(reverse('timetracking_worker', args=[another_worker.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_custom_report_period_en(self):
        response = self.client.get(reverse('timetracking_worker', args=[self.worker.pk]), {
            'period': '01/2010'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['report_period'].month, 1)
        self.assertEqual(response.context['report_period'].year, 2010)

    def test_custom_report_period_de(self):
        self.user.language = 'de'
        self.user.save()
        response = self.client.get(reverse('timetracking_worker', args=[self.worker.pk]), {
            'period': '01.2010'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['report_period'].month, 1)
        self.assertEqual(response.context['report_period'].year, 2010)

    def test_create_manual_timer_invalid_form(self):
        response = self.client.post(reverse('timetracking_worker', args=[self.worker.pk]), {
            'worker': self.worker.pk,
            'start': '01/18/2017 09:00',
            'end': '01/18/2017 8:00',
            'kind': 'work'
        }, HTTP_REFERER=reverse('timetracking'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.context['form'].is_valid())

    def test_create_manual_timer_happy_path_w_breaks_en(self):
        self.assertEqual(Timer.objects.count(), 0)
        response = self.client.post(reverse('timetracking_worker', args=[self.worker.pk]), {
            'worker': self.worker.pk,
            'started': '01/18/2017 08:00',
            'stopped': '01/18/2017 17:00',
            'lunch_break': 't',
            'morning_break': 't',
            'kind': 'work'
        }, HTTP_REFERER=reverse('timetracking'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Timer.objects.count(), 3)

    def test_create_manual_timer_happy_path_w_breaks_de(self):
        self.user.language = 'de'
        self.user.save()
        self.assertEqual(Timer.objects.count(), 0)
        response = self.client.post(reverse('timetracking_worker', args=[self.worker.pk]), {
            'worker': self.worker.pk,
            'started': '18.01.2017 08:00',
            'stopped': '18.01.2017 17:00',
            'lunch_break': 't',
            'morning_break': 't',
            'kind': 'work'
        }, HTTP_REFERER=reverse('timetracking'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Timer.objects.count(), 3)


class TimerDeleteViewTest(ClientTestCase):

    def test_delete_single_timer(self):
        day = timezone.now().replace(day=1, hour=18, minute=0, second=0, microsecond=0)
        timer0 = Timer.objects.create(
            worker=self.worker,
            started=day - timedelta(hours=10),
            stopped=day - timedelta(hours=3)
        )
        self.client.get(reverse('timer.delete', args=[timer0.id]), follow=True)
        post_response = self.client.post(reverse('timer.delete', args=[timer0.id]), follow=True)
        self.assertRedirects(post_response, reverse('timetracking_worker', args=[self.worker.id]), status_code=302)
        self.assertFalse(Timer.objects.exists())

    def test_delete_complete_day(self):
        day = timezone.now().replace(day=1, hour=18, minute=0, second=0, microsecond=0)
        Timer.objects.create(
            worker=self.worker,
            started=day - timedelta(hours=11),
            stopped=day - timedelta(hours=2)
        )
        Timer.objects.create(
            worker=self.worker,
            started=day - timedelta(hours=8),
            stopped=day - timedelta(hours=4)
        )
        Timer.objects.create(
            worker=self.worker,
            started=day - timedelta(hours=3),
            stopped=day - timedelta(hours=1)
        )
        self.client.get(reverse(
            'timer.delete.selected_day',
            args=[day.date().isoformat(), self.worker.id]
        ), follow=True)
        post_response = self.client.post(reverse(
            'timer.delete.selected_day',
            args=[day.date().isoformat(), self.worker.id]
        ), follow=True)
        self.assertRedirects(post_response, reverse(
            'timetracking_worker', args=[self.worker.id]
        ), status_code=302)
        self.assertFalse(Timer.objects.exists())