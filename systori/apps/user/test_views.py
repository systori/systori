from decimal import Decimal
from datetime import date, time
from django.urls import reverse
from allauth.account.models import EmailAddress, EmailConfirmationHMAC

from systori.lib.testing import SystoriTestCase, ClientTestCase
from .models import User
from .factories import UserFactory


class TestWorkersList(ClientTestCase):

    def test_list(self):
        response = self.client.get(reverse('users'))
        self.assertEqual(len(response.context['access_list']), 1)


class TestCreateWorker(ClientTestCase):

    def test_get(self):
        response = self.client.get(reverse('user.add'))
        self.assertTrue(response.context['user_form'])
        self.assertTrue(response.context['worker_form'])
        self.assertTrue(response.context['contract_form'])

    def test_blank_forms(self):
        response = self.client.post(reverse('user.add'))
        self.assertEqual(200, response.status_code)

        user_form = response.context['user_form']
        self.assertFalse(user_form.is_valid())
        self.assertEqual(user_form.errors, {
            'first_name': ['This field is required.']
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

    def test_user_already_member(self):
        response = self.client.post(reverse('user.add'), {
            'first_name': 'Bob',
            'email': self.user.email,
            'rate': '15.35',
            'rate_type': 'hourly',
            'vacation': '20',
            'effective': '2014-12-2',
            'work_start': '9:00',
            'work_end': '17:00',
            'abandoned_timer_penalty': '-1',
        })
        self.assertEqual(200, response.status_code)
        user_form = response.context['user_form']
        self.assertFalse(user_form.is_valid())
        self.assertEqual(user_form.errors, {
            'email': ['User with this email is already a member of this company.']
        })

    def test_successful_add_existing_user(self):
        user2 = UserFactory(first_name='NotChanged', language='en', password=self.password)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.company.workers.count(), 1)
        response = self.client.post(reverse('user.add'), {
            'first_name': 'ChangingItToBob',
            'email': user2.email,
            'rate': '15.35',
            'rate_type': 'hourly',
            'vacation': '20',
            'effective': '2014-12-2',
            'work_start': '9:00',
            'work_end': '17:00',
            'abandoned_timer_penalty': '-1',
        })
        self.assertRedirects(response, reverse('users'))
        # same number of total users but one extra worker in company
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.company.workers.count(), 2)
        user2.refresh_from_db()
        self.assertEqual(user2.first_name, 'NotChanged')

    def test_successful_create_and_add(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.company.workers.count(), 1)
        response = self.client.post(reverse('user.add'), {
            'first_name': 'Fred',
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
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.company.workers.count(), 2)

        user = User.objects.get(email='user@test.com')
        worker = user.access.first()
        contract = worker.contract
        self.assertEqual(contract.rate, Decimal('15.35'))
        self.assertEqual(contract.vacation, 20 * 60)
        self.assertEqual(contract.abandoned_timer_penalty, -60)
        self.assertEqual(contract.effective, date(2014, 12, 2))
        self.assertEqual(contract.work_start, time(9, 00))
        self.assertEqual(contract.work_end, time(17, 00))

    def test_add_without_email(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.company.workers.count(), 1)
        response = self.client.post(reverse('user.add'), {
            'first_name': 'Fred',
            'rate': '15.35',
            'rate_type': 'hourly',
            'vacation': '20',
            'effective': '2014-12-2',
            'work_start': '9:00',
            'work_end': '17:00',
            'abandoned_timer_penalty': '-1',
        })
        self.assertRedirects(response, reverse('users'))
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.company.workers.count(), 2)

        worker = User.objects.get(first_name='Fred').access.first()
        self.assertEqual(worker.company, self.company)


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

    def test_get_verified(self):
        EmailAddress.objects.create(user=self.user, verified=True)
        response = self.client.get(reverse('user.edit', args=[self.user.id]))
        self.assertFalse(response.context['user_form'])
        self.assertTrue(response.context['worker_form'])
        self.assertTrue(response.context['contract_form'])

    def test_successful_edit_of_unverified(self):
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

    def test_successful_edit_of_verified(self):
        EmailAddress.objects.create(user=self.user, verified=True)
        original_first_name = self.user.first_name
        attempted_first_name = 'ChangedName'
        self.assertNotEqual(original_first_name, attempted_first_name)
        response = self.client.post(reverse('user.edit', args=[self.user.id]), {
            'first_name': attempted_first_name,
            'is_staff': 'True',
            'can_track_time': 'True',
            'rate': '77',
            'rate_type': 'hourly',
            'vacation': '21',
            'effective': '2014-12-2',
            'work_start': '9:00',
            'work_end': '17:00',
            'abandoned_timer_penalty': '0',
        })
        self.assertRedirects(response, reverse('users'))

        # was able to change rate but not first_name
        user = User.objects.get(first_name=original_first_name)
        contract = user.access.first().contract
        self.assertEqual(contract.rate, Decimal('77.0'))


class TestRegistration(SystoriTestCase):

    def test_on_boarding_workflow(self):

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

        self.assertContains(self.client.get(reverse('company.create')), 'Subdomain')
        response = self.client.post(reverse('company.create'), {
            'name': 'Widgets LLC',
            'schema': 'widgets',
            'timezone': 'Europe/Berlin'
        }, follow=True, HTTP_HOST='widgets.systori.localhost')
        self.assertRedirects(response, 'http://widgets.systori.localhost')
        self.assertContains(response, 'Widgets LLC')


class TestTokenAuth(ClientTestCase):

    def test_obtain_and_check_token(self):
        user = UserFactory(first_name='FirstName', language='en', password="pass", company=self.company)
        response = self.client.post(reverse('drf.tokenauth'), {
            'username': user.email,
            'password': "pass"
        }, headers={
            'Content-Type': 'application/json'
        })
        self.assertEqual(response.status_code, 200)
        token = response.data['token']
        response = self.client.get(reverse('api.project.available', args=[1]),
                                   HTTP_AUTHORIZATION = 'Token {}'.format(token))
        self.assertEqual(response.status_code, 200)
