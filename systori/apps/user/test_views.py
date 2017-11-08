from decimal import Decimal
from datetime import date, time
from django.urls import reverse
from allauth.account.models import EmailConfirmationHMAC

from systori.lib.testing import SystoriTestCase, ClientTestCase
from .models import User


class TestWorkersList(ClientTestCase):

    def test_list(self):
        response = self.client.get(reverse('users'))
        self.assertEqual(len(response.context['access_list']), 1)


class TestCreateWorker(ClientTestCase):

    def test_get(self):
        response = self.client.get(reverse('user.add'))
        self.assertIn('user_form', response.context)
        self.assertIn('worker_form', response.context)
        self.assertIn('contract_form', response.context)

    def test_blank_forms(self):
        response = self.client.post(reverse('user.add'))
        self.assertEqual(200, response.status_code)

        user_form = response.context['user_form']
        self.assertFalse(user_form.is_valid())
        self.assertEqual(user_form.errors, {
            '__all__': ['A name or email is required.']
        })

        worker_form = response.context['worker_form']
        self.assertTrue(worker_form.is_valid())

        contract_form = response.context['contract_form']
        self.assertFalse(contract_form.is_valid())
        self.assertDictEqual(contract_form.errors, {
            'rate': ['This field is required.'],
            'rate_type': ['This field is required.'],
            'vacation': ['This field is required.'],
            'effective': ['This field is required.'],
            'work_start': ['This field is required.'],
            'work_end': ['This field is required.'],
            'abandoned_timer_penalty': ['This field is required.'],
        })

    def test_worker_exists(self):
        response = self.client.post(reverse('user.add'), {
            'email': self.user.email
        })
        self.assertEqual(200, response.status_code)
        user_form = response.context['user_form']
        self.assertFalse(user_form.is_valid())
        self.assertEqual(user_form.errors, {
            'email': ['User with this Email address already exists.']
        })

    def test_successful_create(self):
        response = self.client.post(reverse('user.add'), {
            'email': 'user@test.com',
            'rate': '15.35',
            'rate_type': 'hourly',
            'vacation': '20',
            'effective': '2014-12-2',
            'work_start': '9:00',
            'work_end': '17:00',
            'abandoned_timer_penalty': '-1',
        })
        self.assertRedirects(response, reverse('users'))

        user = User.objects.get(email='user@test.com')
        worker = user.access.first()
        contract = worker.contract
        self.assertEqual(contract.rate, Decimal('15.35'))
        self.assertEqual(contract.vacation, 20 * 60)
        self.assertEqual(contract.abandoned_timer_penalty, -60)
        self.assertEqual(contract.effective, date(2014, 12, 2))
        self.assertEqual(contract.work_start, time(9, 00))
        self.assertEqual(contract.work_end, time(17, 00))


class TestEditWorker(ClientTestCase):

    def test_get(self):
        response = self.client.get(reverse('user.edit', args=[self.user.id]))
        user_form = response.context['user_form']
        worker_form = response.context['worker_form']
        contract_form = response.context['contract_form']
        self.assertEqual(user_form.instance, self.user)
        self.assertEqual(worker_form.instance, self.worker)
        self.assertEqual(contract_form.instance, self.worker.contract)
        self.assertEqual(contract_form['vacation'].value(), 20.0)

    def test_successful_edit(self):
        response = self.client.post(reverse('user.edit', args=[self.user.id]), {
            'first_name': 'Bob',
            'is_staff': 'True',
            'can_track_time': 'True',
            'rate': '16',
            'rate_type': 'hourly',
            'vacation': '21',
            'effective': '2014-12-2',
            'work_start': '9:00',
            'work_end': '17:00',
            'abandoned_timer_penalty': '0',
        })
        self.assertRedirects(response, reverse('users'))

        user = User.objects.get(first_name='Bob')
        worker = user.access.first()
        self.assertEqual(worker.can_track_time, True)
        contract = worker.contract
        self.assertEqual(contract.rate, Decimal('16.0'))
        self.assertEqual(contract.vacation, 21 * 60)
        self.assertEqual(contract.abandoned_timer_penalty, 0)


class TestRegistration(SystoriTestCase):

    def test_onboarding_workflow(self):

        # main page has registration link
        self.assertContains(self.client.get('', follow=True), reverse('account_signup'))

        # user fills out registration form
        self.assertContains(self.client.get(reverse('account_signup')), 'Vorname')
        response = self.client.post(reverse('account_signup'), {
            'first_name': 'Bob',
            'last_name': 'Jones',
            'email': 'bob@systori.com',
            'password1': 'the password open sesame',
            'password2': 'the password open sesame',
        })
        self.assertRedirects(response, reverse('account_email_verification_sent'))
        user = User.objects.get(first_name='Bob')
        self.assertEqual(user.last_name, 'Jones')
        self.assertEqual(user.email, 'bob@systori.com')
        self.assertEqual(user.access.count(), 0)

        # user clicks on link in their email verification link
        confirmation = EmailConfirmationHMAC(user.emailaddress_set.get())
        self.client.post(reverse('account_confirm_email', args=[confirmation.key]))

        response = self.client.post(reverse('account_login'), {
            'login': 'bob@systori.com',
            'password': 'the password open sesame',
        }, follow=True)
        self.assertRedirects(response, reverse('companies'))
        self.assertContains(response, reverse('company.create'))

        self.assertContains(self.client.get(reverse('company.create')), 'Sub-Domain')
        response = self.client.post(reverse('company.create'), {
            'name': 'Widgets LLC',
            'schema': 'widgets',
            'timezone': 'Europe/Berlin'
        }, follow=True, HTTP_HOST='widgets.systori.localhost')
        self.assertRedirects(response, reverse('companies'))
        self.assertContains(response, 'Widgets LLC')
