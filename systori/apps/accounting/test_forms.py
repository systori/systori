from django.test import TestCase
from django.utils.translation import activate

from ..directory.models import Contact, ProjectContact
from .test_workflow import create_data, A
from .forms import *
from .models import Entry


class TestForm(TestCase):
    model = None
    form = None
    form_set = None

    def setUp(self):
        # creates task with 480 net and 571.20 gross ready to be billed
        activate('en')
        create_data(self)
        ProjectContact.objects.create(
            project=self.project,
            contact=Contact.objects.create(first_name="Ludwig", last_name="von Mises"),
            association=ProjectContact.CUSTOMER,
            is_billable=True
        )
        self.task.complete = 5
        self.task.save()

    def make_form(self, data=None, initial={}, json=None, txn=None):

        if txn:
            instance = self.model(project=self.project, json=json or {'jobs': []}, transaction=txn)
        else:
            instance = self.model(project=self.project, json=json or {'jobs': []})
        jobs = self.project.jobs.all()

        if data:
            _form_set = self.form_set(instance=instance, jobs=jobs)
            for key, value in _form_set.management_form.initial.items():
                data['job-'+key] = value

        return self.form(instance=instance, jobs=jobs, initial=initial, data=data)

    def assert_all_forms_valid(self, form):
        self.assertIsNotNone(form.data)  # need data in order for is_valid() to even work
        self.assertTrue(form.formset.management_form.is_valid(), form.formset.management_form.errors)
        self.assertTrue(form.formset.is_valid(), form.formset.errors)
        self.assertTrue(form.is_valid(), form.errors)


class InvoiceFormTests(TestForm):
    model = Invoice
    form = InvoiceForm
    form_set = InvoiceFormSet

    def test_simple_invoice_form_is_valid(self):
        form = self.make_form({

            'title': 'Invoice #1',
            'header': 'The Header',
            'footer': 'The Footer',
            'invoice_no': '2015/01/01',

            'job-0-is_invoiced': 'True',
            'job-0-job_id': self.job.id,
            'job-0-debit_net': '1',
            'job-0-debit_tax': '1',

            'job-1-is_invoiced': 'True',
            'job-1-job_id': self.job2.id,
            'job-1-debit_net': '1',
            'job-1-debit_tax': '1',

        })
        self.assert_all_forms_valid(form)
        self.assertEqual(D('4'), form.debit_total_amount.gross)

    def test_corrupted_form_job_list(self):
        # change order of the jobs
        form = self.make_form({

            'title': 'Invoice #1',
            'header': 'The Header',
            'footer': 'The Footer',
            'invoice_no': '2015/01/01',

            'job-0-is_invoiced': 'True',
            'job-0-job_id': self.job2.id,
            'job-0-debit_net': '1',
            'job-0-debit_tax': '1',

            'job-1-is_invoiced': 'True',
            'job-1-job_id': self.job.id,
            'job-1-debit_net': '1',
            'job-1-debit_tax': '1',

        })
        self.assertFalse(form.formset.is_valid())
        self.assertIn('Form has become invalid due to external changes to the jobs list.',
                      form.formset.non_form_errors())

    def test_initial_form_has_debit(self):
        form = self.make_form().formset[0]
        self.assertTrue(form.is_itemized)
        self.assertEqual(D('480.00'), form['debit_net'].value())
        self.assertEqual(D('571.20'), form.debit_amount.gross)

    def test_initial_form_no_debit(self):
        debit_jobs([(self.job, A(571.20), Entry.WORK_DEBIT)])
        # now there is nothing new to invoice, we invoiced the full amount already
        form = self.make_form().formset[0]
        self.assertTrue(form.is_itemized)
        self.assertEqual(D('0.00'), form['debit_net'].value())
        self.assertEqual(D('0.00'), form.debit_amount.gross)

    def test_override_debit(self):
        job_json = {'job.id': self.job.id, 'is_override': 'True', 'debit': A(119.00)}
        form = self.make_form(json={'jobs': [job_json]}).formset[0]
        self.assertFalse(form.is_itemized)
        self.assertEqual(D('100.00'), form['debit_net'].value())
        self.assertEqual(D('119.00'), form.debit_amount.gross)

    def test_stale_debit_gets_updated(self):
        # just like above test, but now is_override == False
        job_json = {'job.id': self.job.id, 'debit': A(119.00)}
        form = self.make_form(json={'jobs': [job_json]}).formset[0]
        self.assertTrue(form.is_itemized)
        self.assertEqual(D('480.00'), form['debit_net'].value())
        self.assertEqual(D('571.20'), form.debit_amount.gross)

    def test_transaction_gets_rolled_back_to_calculate_debit(self):
        # just like test_initial_no_debit_no_txn, but with transaction present
        txn = debit_jobs([(self.job, A(571.20), Entry.WORK_DEBIT)])
        # debit will get deleted and rollback to get previous accounting state
        form = self.make_form(txn=txn).formset[0]
        self.assertTrue(form.is_itemized)
        self.assertEqual(D('480.00'), form['debit_net'].value())
        self.assertEqual(D('571.20'), form.debit_amount.gross)


class PaymentFormTests(TestForm):
    model = Payment
    form = PaymentForm
    form_set = PaymentFormSet

    def test_simple_split_is_valid(self):
        form = self.make_form({

            'bank_account': Account.objects.banks().first().id,
            'payment': '4',
            'discount': '0.00',
            'document_date': '2015-01-01',

            'job-0-job_id': self.job.id,
            'job-0-split_net': '1',
            'job-0-split_tax': '1',
            'job-0-discount_net': '0',
            'job-0-discount_tax': '0',

            'job-1-job_id': self.job2.id,
            'job-1-split_net': '1',
            'job-1-split_tax': '1',
            'job-1-discount_net': '0',
            'job-1-discount_tax': '0',

        })
        self.assert_all_forms_valid(form)
        self.assertEqual(2, len(form.formset.get_json_rows()))

    def test_handling_blank_splits(self):
        form = self.make_form({

            'bank_account': Account.objects.banks().first().id,
            'payment': '2',
            'discount': '0.00',
            'document_date': '2015-01-01',

            'job-0-job_id': self.job.id,
            'job-0-split_net': '1',
            'job-0-split_tax': '1',
            'job-0-discount_net': '0',
            'job-0-discount_tax': '0',

            'job-1-job_id': self.job2.id,
            'job-1-split_net': '',
            'job-1-split_tax': '',
            'job-1-discount_net': '0',
            'job-1-discount_tax': '0',

        })
        self.assert_all_forms_valid(form)
        self.assertEqual(1, len(form.formset.get_json_rows()))

    def test_all_amounts_blank(self):
        form = self.make_form({

            'bank_account': Account.objects.banks().first().id,
            'payment': '',
            'discount': '0.00',
            'document_date': '2015-01-01',

            'job-0-job_id': self.job.id,
            'job-0-split_net': '',
            'job-0-split_tax': '',
            'job-0-discount_net': '',
            'job-0-discount_tax': '',

            'job-1-job_id': self.job2.id,
            'job-1-split_net': '',
            'job-1-split_tax': '',
            'job-1-discount_net': '',
            'job-1-discount_tax': '',

        })
        self.assertTrue(form.formset.is_valid(), form.formset.errors)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(['payment'], list(form.errors.keys()))
        self.assertEqual(0, len(form.formset.get_json_rows()))


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

