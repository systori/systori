from decimal import Decimal as D
from django.test import TestCase
from django.utils.translation import activate
from .test_workflow import create_data
from .forms import *
from .models import Entry


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


class DebitFormTests(TestCase):

    def setUp(self):
        # creates task with 480 net and 571.20 gross ready to be billed
        create_data(self)
        self.task.complete = 5
        self.task.save()

    def test_initial_load_not_booked(self):
        form = DebitForm(initial={'job': self.job, 'is_invoiced': True, 'is_booked': False})
        self.assertEqual(D('480.00'), form['amount_net'].value())
        self.assertEqual(D('571.20'), form['amount_gross'].value())

    def test_initial_load_nothing_to_bill(self):
        debit_jobs([(self.job, D(571.20), Entry.WORK_DEBIT)])
        # now there is nothing new to invoice, we invoiced the full amount already
        # is_booked: False, means this form is not associated with the previous debit
        form = DebitForm(initial={'job': self.job, 'is_invoiced': True, 'is_booked': False})
        self.assertEqual(D('0.00'), form['amount_net'].value())
        self.assertEqual(D('0.00'), form['amount_gross'].value())

    def test_reload_with_amount_changed_not_booked(self):
        form = DebitForm(
            data={'is_invoiced': True, 'job': self.job.id, 'amount_net': '100.00', 'amount_gross': '119.00'},
            initial={'job': self.job, 'is_invoiced': True, 'is_booked': False}
        )
        form.full_clean()
        initial = form.get_initial()
        initial['is_booked'] = False
        reloaded = DebitForm(initial=initial)
        self.assertEqual(D('480.00'), reloaded['amount_net'].value())
        self.assertEqual(D('571.20'), reloaded['amount_gross'].value())
        # this would happen in real life if while you're filling out the invoice form
        # somebody marks a task complete, so upon refresh of form it will show the change
        self.assertEqual(D('380.00'), reloaded.diff_debit_amount_net)

    def test_initial_load_after_booking(self):
        debit_jobs([(self.job, D(571.20), Entry.WORK_DEBIT)])
        # is_booked: True, means this form is associated with the previous debit
        form = DebitForm(initial={'job': self.job, 'is_invoiced': True, 'is_booked': True,
                                  'amount_net': '480.00', 'amount_gross': '571.20',
                                  'debited_gross': '571.20', 'balance_gross': '571.20',
                                  'estimate_net': '480.00', 'itemized_net': '480.00'})
        self.assertEqual(D('480.00'), form['amount_net'].value())
        self.assertEqual(D('571.20'), form['amount_gross'].value())

    def test_initial_load_after_booking_with_net_increase(self):
        debit_jobs([(self.job, D(452.20), Entry.WORK_DEBIT)])
        # is_booked: True, means this form is associated with the previous debit
        form = DebitForm(initial={'job': self.job, 'is_invoiced': True, 'is_booked': True,
                                  'amount_net': '380.00', 'amount_gross': '452.20',
                                  'debited_gross': '452.20', 'balance_gross': '452.20',
                                  'estimate_net': '960.00', 'itemized_net': '380.00'})
        self.assertEqual(D('480.00'), form['amount_net'].value())
        self.assertEqual(D('571.20'), form['amount_gross'].value())
        self.assertEqual(D('100.00'), form.diff_debit_amount_net)
        self.assertEqual(D('119.00'), form.diff_debited_gross)
        self.assertEqual(D('0.00'), form.diff_estimate_net)
        self.assertEqual(D('100.00'), form.diff_itemized_net)

