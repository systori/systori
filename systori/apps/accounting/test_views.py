from datetime import date
from decimal import Decimal

from django.core.urlresolvers import reverse

from systori.lib.testing import SystoriTestCase
from systori.lib.accounting.tools import Amount
from .models import Account
from ..accounting.test_workflow import create_data
from ..directory.models import Contact, ProjectContact
from ..document.models import Invoice, Payment, Adjustment, Refund
from .forms import InvoiceForm, InvoiceFormSet
from .forms import PaymentForm, PaymentFormSet
from .forms import AdjustmentForm, AdjustmentFormSet
from .forms import RefundForm, RefundFormSet


class DocumentTestCase(SystoriTestCase):

    def setUp(self):
        super().setUp()
        create_data(self)
        ProjectContact.objects.create(
            project=self.project,
            contact=Contact.objects.create(first_name="Ludwig", last_name="von Mises"),
            association=ProjectContact.CUSTOMER,
            is_billable=True
        )
        self.client.login(username=self.user.email, password='open sesame')

    def make_management_form(self):
        data = {}
        instance = self.model(project=self.project, json={'jobs': []})
        jobs = self.project.jobs.all()
        _form_set = self.form_set(instance=instance, jobs=jobs)
        for key, value in _form_set.management_form.initial.items():
            data['job-'+key] = value
        return data

    def form_data(self, data):
        data.update(self.make_management_form())
        return data


class InvoiceViewTests(DocumentTestCase):
    model = Invoice
    form = InvoiceForm
    form_set = InvoiceFormSet

    def setUp(self):
        super().setUp()
        self.task.complete = 5
        self.task.save()

    def test_happy_path_create_update_and_render(self):

        data = {
            'title': 'Invoice #1',
            'header': 'The Header',
            'footer': 'The Footer',
            'invoice_no': '2015/01/01',
            'document_date': '2015-01-01',

            'job-0-is_invoiced': 'True',
            'job-0-job_id': self.job.id,
            'job-0-debit_net': '1',
            'job-0-debit_tax': '1',

            'job-1-is_invoiced': 'True',
            'job-1-job_id': self.job2.id,
            'job-1-debit_net': '1',
            'job-1-debit_tax': '1',
        }
        data.update(self.make_management_form())
        response = self.client.post(reverse('invoice.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        response = self.client.get(reverse('invoice.pdf', args=[
            self.project.id,
            'print',
            Invoice.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)

        data = {
            'title': 'Invoice #1',
            'header': 'new header',
            'footer': 'new footer',
            'invoice_no': '2015/01/01',
            'document_date': '2015-07-28',

            'job-0-is_invoiced': 'True',
            'job-0-job_id': self.job.id,
            'job-0-debit_net': '5',
            'job-0-debit_tax': '5',

            'job-1-is_invoiced': 'True',
            'job-1-job_id': self.job2.id,
            'job-1-debit_net': '5',
            'job-1-debit_tax': '5',
        }
        data.update(self.make_management_form())
        invoice = Invoice.objects.order_by('id').first()
        response = self.client.post(reverse('invoice.update', args=[self.project.id, invoice.id]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        invoice.refresh_from_db()
        self.assertEqual(invoice.document_date, date(2015, 7, 28))
        self.assertEqual(invoice.json['header'], 'new header')
        self.assertEqual(invoice.json['footer'], 'new footer')


class PaymentViewTests(DocumentTestCase):
    model = Payment
    form = PaymentForm
    form_set = PaymentFormSet

    def setUp(self):
        super().setUp()
        self.task.complete = 5
        self.task.save()

    def test_happy_path_create_update_and_render(self):

        data = {
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
        }
        data.update(self.make_management_form())
        response = self.client.post(reverse('payment.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        response = self.client.get(reverse('payment.pdf', args=[
            self.project.id,
            'print',
            Payment.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)

        payment = Payment.objects.order_by('id').first()
        self.assertEqual(payment.document_date, date(2015, 1, 1))
        self.assertEqual(payment.json['payment'], Decimal('4.0'))

        data = {
            'bank_account': Account.objects.banks().first().id,
            'payment': '6',
            'discount': '0.00',
            'document_date': '2015-07-28',

            'job-0-job_id': self.job.id,
            'job-0-split_net': '2',
            'job-0-split_tax': '1',
            'job-0-discount_net': '0',
            'job-0-discount_tax': '0',

            'job-1-job_id': self.job2.id,
            'job-1-split_net': '2',
            'job-1-split_tax': '1',
            'job-1-discount_net': '0',
            'job-1-discount_tax': '0',
        }
        data.update(self.make_management_form())
        response = self.client.post(reverse('payment.update', args=[self.project.id, payment.id]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        payment.refresh_from_db()
        self.assertEqual(payment.document_date, date(2015, 7, 28))
        self.assertEqual(payment.json['payment'], Decimal('6.0'))


class AdjustmentViewTests(DocumentTestCase):
    model = Adjustment
    form = AdjustmentForm
    form_set = AdjustmentFormSet

    def setUp(self):
        super().setUp()
        self.task.complete = 5
        self.task.save()

    def test_happy_path_create_update_and_render(self):

        data = {
            'title': 'Adjustment #1',
            'header': 'The Header',
            'footer': 'The Footer',
            'document_date': '2015-01-01',

            'job-0-job_id': self.job.id,
            'job-0-adjustment_net': '1',
            'job-0-adjustment_tax': '1',

            'job-1-job_id': self.job2.id,
            'job-1-adjustment_net': '1',
            'job-1-adjustment_tax': '1',
        }
        data.update(self.make_management_form())
        response = self.client.post(reverse('adjustment.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        response = self.client.get(reverse('adjustment.pdf', args=[
            self.project.id,
            'print',
            Adjustment.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)

        data = {
            'title': 'Adjustment #1',
            'header': 'new header',
            'footer': 'new footer',
            'document_date': '2015-07-28',

            'job-0-job_id': self.job.id,
            'job-0-adjustment_net': '5',
            'job-0-adjustment_tax': '5',

            'job-1-job_id': self.job2.id,
            'job-1-adjustment_net': '5',
            'job-1-adjustment_tax': '5',
        }
        data.update(self.make_management_form())
        adjustment = Adjustment.objects.order_by('id').first()
        response = self.client.post(reverse('adjustment.update', args=[self.project.id, adjustment.id]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        adjustment.refresh_from_db()
        self.assertEqual(adjustment.document_date, date(2015, 7, 28))
        self.assertEqual(adjustment.json['header'], 'new header')
        self.assertEqual(adjustment.json['footer'], 'new footer')


class RefundViewTests(DocumentTestCase):
    model = Refund
    form = RefundForm
    form_set = RefundFormSet

    def setUp(self):
        super().setUp()
        self.task.complete = 5
        self.task.save()

    def test_happy_path_create_update_and_render(self):

        data = {
            'title': 'Refund #1',
            'header': 'new header',
            'footer': 'new footer',
            'document_date': '2015-01-01',

            'job-0-job_id': self.job.id,
            'job-0-refund_net': '1',
            'job-0-refund_tax': '1',
            'job-0-credit_net': '0',
            'job-0-credit_tax': '0',

            'job-1-job_id': self.job2.id,
            'job-1-refund_net': '0',
            'job-1-refund_tax': '0',
            'job-1-credit_net': '1',
            'job-1-credit_tax': '1',
        }
        data.update(self.make_management_form())
        response = self.client.post(reverse('refund.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        response = self.client.get(reverse('refund.pdf', args=[
            self.project.id,
            'print',
            Refund.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)

        refund = Refund.objects.order_by('id').first()
        self.assertEqual(refund.document_date, date(2015, 1, 1))
        self.assertEqual(refund.json['refund_total'], Amount(Decimal('1.0'), Decimal('1.0')))
        self.assertEqual(refund.json['credit_total'], Amount(Decimal('1.0'), Decimal('1.0')))

        data = {
            'title': 'Refund #1',
            'header': 'updated header',
            'footer': 'updated footer',
            'document_date': '2015-07-28',

            'job-0-job_id': self.job.id,
            'job-0-refund_net': '2',
            'job-0-refund_tax': '2',
            'job-0-credit_net': '0',
            'job-0-credit_tax': '0',

            'job-1-job_id': self.job2.id,
            'job-1-refund_net': '0',
            'job-1-refund_tax': '0',
            'job-1-credit_net': '2',
            'job-1-credit_tax': '2',
        }
        data.update(self.make_management_form())
        response = self.client.post(reverse('refund.update', args=[self.project.id, refund.id]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        refund.refresh_from_db()
        self.assertEqual(refund.document_date, date(2015, 7, 28))
        self.assertEqual(refund.json['refund_total'], Amount(Decimal('2.0'), Decimal('2.0')))
        self.assertEqual(refund.json['credit_total'], Amount(Decimal('2.0'), Decimal('2.0')))


class AccountingViewTests(DocumentTestCase):
    def test_accounts_list(self):
        response = self.client.get(reverse('accounts'))
        self.assertEqual(200, response.status_code)
