from django.test import TestCase
from django.utils.translation import activate
from .test_accounting import create_data
from .forms import *


class TestBankAccountForm(TestCase):
    def setUp(self):
        create_data(self)

    def test_form_initial_incremented_code(self):
        self.assertEquals(str(BANK_CODE_RANGE[0] + 1), BankAccountForm().initial['code'])

    def test_form_edit_code(self):
        self.assertEquals("hi", BankAccountForm(instance=Account.objects.create(code="hi")).initial['code'])

    def test_valid_code(self):
        self.assertTrue(BankAccountForm({'code': '1200'}).is_valid())
        self.assertTrue(BankAccountForm({'code': '1288'}).is_valid())

    def test_invalid_code(self):
        activate('en')
        self.assertFalse(BankAccountForm({'code': 'foo'}).is_valid())
        self.assertFalse(BankAccountForm({'code': '1199'}).is_valid())
        self.assertFalse(BankAccountForm({'code': '1289'}).is_valid())

        form = BankAccountForm({'code': '1a'})
        self.assertEquals('Account code must be a number between 1200 and 1288 inclusive.', form.errors['code'][0])


class AccountingTestCase(TestCase):

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()

        self.management_form = {}
        _management_form = SplitPaymentFormSet(jobs=self.project.jobs.all()).management_form.initial
        for key, value in _management_form.items():
            self.management_form['split-'+key] = value

    def make_split_payment_form(self, data):
        data.update(self.management_form)
        return SplitPaymentFormSet(data=data, jobs=self.project.jobs.all())


class PaymentSplitFormTests(AccountingTestCase):

    def test_simple_split_is_valid(self):
        form = self.make_split_payment_form({

            'bank_account': Account.objects.banks().first().id,
            'amount': '2',
            'transacted_on': '2015-01-01',

            'split-0-job': self.job.id,
            'split-0-amount': '1',
            'split-0-discount': '0',

            'split-1-job': self.job2.id,
            'split-1-amount': '1',
            'split-1-discount': '0',

        })
        self.assertTrue(form.is_valid())
        self.assertEqual(2, len(form.get_splits()))

    def test_handling_blank_splits(self):
        form = self.make_split_payment_form({

            'bank_account': Account.objects.banks().first().id,
            'amount': '2',
            'transacted_on': '2015-01-01',

            'split-0-job': self.job.id,
            'split-0-amount': '2',
            'split-0-discount': '0',

            'split-1-job': self.job2.id,
            'split-1-amount': '',
            'split-1-discount': '0',

        })
        self.assertTrue(form.is_valid())
        self.assertEqual(1, len(form.get_splits()))

    def test_all_amounts_blank(self):
        form = self.make_split_payment_form({

            'bank_account': Account.objects.banks().first().id,
            'amount': '',
            'transacted_on': '2015-01-01',

            'split-0-job': self.job.id,
            'split-0-amount': '',
            'split-0-discount': '0',

            'split-1-job': self.job2.id,
            'split-1-amount': '',
            'split-1-discount': '0',

        })
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.payment_form.errors))
        self.assertEqual(0, len(form.non_form_errors()))
        self.assertEqual(0, len(form.get_splits()))
