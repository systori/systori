from datetime import date, datetime, timedelta
from decimal import Decimal
from PyPDF2 import PdfFileReader
from io import BytesIO
from textwrap import dedent
from freezegun import freeze_time

from django.utils import timezone
from django.urls import reverse

from systori.lib.testing import ClientTestCase
from systori.lib.accounting.tools import Amount

from ..project.factories import ProjectFactory
from ..task.factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory
from ..directory.factories import ContactFactory

from ..timetracking.models import Timer
from ..accounting.models import Account, create_account_for_job
from ..accounting.workflow import create_chart_of_accounts

from .forms import InvoiceForm, InvoiceFormSet
from .forms import PaymentForm, PaymentFormSet
from .forms import AdjustmentForm, AdjustmentFormSet
from .forms import RefundForm, RefundFormSet
from .forms import ProposalForm, ProposalFormSet
from .models import Invoice, Payment, Adjustment, Refund
from .models import Proposal, Letterhead, Timesheet
from .factories import InvoiceFactory, LetterheadFactory


class DocumentTestCase(ClientTestCase):
    model = None
    form = None
    form_set = None

    def setUp(self):
        super().setUp()

        self.project = ProjectFactory()

        self.contact = ContactFactory(
            salutation='Professor',
            first_name='Ludwig',
            last_name='von Mises',
            project=self.project,
            is_billable=True
        )

        create_chart_of_accounts(self)

        self.job = JobFactory(name='Job One', project=self.project)
        self.job.account = create_account_for_job(self.job)
        self.job.save()
        self.group = GroupFactory(parent=self.job)
        self.task = TaskFactory(qty=10, complete=5, price=96, group=self.group)
        self.lineitem = LineItemFactory(task=self.task)

        self.job2 = JobFactory(name='Job Two', project=self.project)
        self.job2.account = create_account_for_job(self.job2)
        self.job2.save()

        self.letterhead = LetterheadFactory(with_settings=True)

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

    def test_happy_path_create_update_and_render(self):

        response = self.client.get(reverse('invoice.create', args=[self.project.id]))
        self.assertEqual(200, response.status_code)

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

    def test_render_simple_invoice(self):
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
            self.project.id, 'print', Invoice.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)

        pdf = PdfFileReader(BytesIO(response.content))
        extractedText = pdf.getPage(0).extractText()
        self.assertEqual(extractedText, dedent(
        """\
        Professor Ludwig von Mises


        Invoice #1
        Jan. 1, 2015
        Invoice No. 2015/01/01
        Please indicate the correct invoice number on your payment.
        The Header

        consideration
        19% tax
        gross
        Project progress
        $2.00
        $2.00
        $4.00
        This Invoice
        $2.00
        $2.00
        $4.00
        The Footer
        Page 1 of 2
        """))


class PaymentViewTests(DocumentTestCase):
    model = Payment
    form = PaymentForm
    form_set = PaymentFormSet

    def test_happy_path_create_update_and_render(self):

        response = self.client.get(reverse('payment.create', args=[self.project.id]))
        self.assertEqual(200, response.status_code)

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

    def test_happy_path_create_update_and_render(self):

        response = self.client.get(reverse('adjustment.create', args=[self.project.id]))
        self.assertEqual(200, response.status_code)

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

    def test_happy_path_create_update_and_render(self):

        response = self.client.get(reverse('refund.create', args=[self.project.id]))
        self.assertEqual(200, response.status_code)

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


class ProposalViewTests(DocumentTestCase):
    model = Proposal
    form = ProposalForm
    form_set = ProposalFormSet

    def test_serialize_n_render_proposal(self):

        response = self.client.get(reverse('proposal.create', args=[self.project.id]))
        self.assertEqual(200, response.status_code)

        data = self.form_data({
            'title': 'Proposal #1',
            'document_date': '2015-01-01',
            'header': 'hello',
            'footer': 'bye',
            'add_terms': True,
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'True',
            'job-1-job_id': self.job2.id,
            'job-1-is_attached': 'True',
        })
        response = self.client.post(reverse('proposal.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        # render

        response = self.client.get(reverse('proposal.pdf', args=[
            self.project.id,
            'print',
            Proposal.objects.first().id
        ]), {'with_lineitems': True})
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse('proposal.pdf', args=[
            self.project.id,
            'email',
            Proposal.objects.first().id
        ]), {'with_lineitems': True})
        self.assertEqual(200, response.status_code)

    def test_serialize_n_render_small_structure(self):
        self.project = ProjectFactory(structure="0.0")
        self.job = JobFactory(project=self.project)
        self.task = TaskFactory(qty=10, complete=5, price=96, group=self.job)

        self.contact = ContactFactory(
            project=self.project,
            is_billable=True
        )

        data = self.form_data({
            'title': 'Proposal #1',
            'document_date': '2015-01-01',
            'header': 'hello',
            'footer': 'bye',
            'add_terms': False,
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'True'
        })
        response = self.client.post(reverse('proposal.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        # render

        response = self.client.get(reverse('proposal.pdf', args=[
            self.project.id,
            'print',
            Proposal.objects.first().id
        ]), {}) # empty {} == 'with_lineitems': False
        extractedText = PdfFileReader(BytesIO(response.content)).getPage(0).extractText()
        for text in ['Proposal', 'hello', 'bye', self.job.name, self.task.name]:
            self.assertTrue(text in extractedText)

    def test_serialize_n_render_big_structure(self):
        self.project = ProjectFactory(structure="0.0.0.0.0.0")
        self.job = JobFactory(project=self.project, generate_groups=True)
        self.task = TaskFactory(qty=10, complete=5, price=96, group=self.job.all_groups.order_by('id').last())
        self.job2 = JobFactory(project=self.project, generate_groups=True)
        for number in range(1,11,1):
            TaskFactory(name="task {}".format(number), qty=10, complete=5, price=96,
                        group=self.job2.all_groups.order_by('id').last())
        TaskFactory(name="task 11", qty=10, complete=5, price=96, is_provisional=True,
                    group=self.job2.all_groups.order_by('id').last())
        TaskFactory(name='window cheap', qty=10, complete=5, price=50, total=500, variant_group=1, variant_serial=0,
                    group=self.job2.all_groups.order_by('id').last())
        TaskFactory(name="window premium", qty=10, complete=5, price=125, total=1250, variant_group=1, variant_serial=1,
                    group=self.job2.all_groups.order_by('id').last())
        group3 = GroupFactory(parent=self.job2.all_groups.order_by('id')[3])
        TaskFactory(name="task 14", qty=10, complete=5, price=96, group=group3)
        for number in range(1,3):
            LineItemFactory(qty=2, price=1.23, unit='m³', task=self.task)

        self.contact = ContactFactory(
            project=self.project,
            is_billable=True
        )

        data = self.form_data({
            'title': 'Proposal #1',
            'document_date': '2015-01-01',
            'header': 'hello',
            'footer': 'bye',
            'add_terms': False,
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'True',
            'job-1-job_id': self.job2.id,
            'job-1-is_attached': 'True'
        })
        response = self.client.post(reverse('proposal.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        # render
        response = self.client.get(reverse('proposal.pdf', args=[
            self.project.id,
            'print',
            Proposal.objects.first().id
        ]), {'with_lineitems': True}) # empty {} == 'with_lineitems': False

        pdfFileObject = PdfFileReader(BytesIO(response.content))
        extractedText = ""
        for page in range(pdfFileObject.getNumPages()):
            extractedText += pdfFileObject.getPage(page).extractText()
        for text in ['Proposal', 'hello', 'bye', 'window premium', 'Optional', self.job.name, self.task.name]:
            self.assertTrue(text in extractedText)

    def test_update_proposal(self):

        proposal = Proposal.objects.create(
            project=self.project,
            letterhead=self.letterhead,
            document_date=timezone.now(),
            json={'header': 'header', 'footer': 'footer', 'total_gross': '0', 'jobs': []},
            notes='notes'
        )
        data = self.form_data({
            'title': 'Proposal #1',
            'document_date': '2015-07-28',
            'header': 'new header',
            'footer': 'new footer',
            'notes': 'new notes',
            'add_terms': True,
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'True',
            'job-1-job_id': self.job2.id,
            'job-1-is_attached': 'True',
        })
        response = self.client.post(reverse('proposal.update', args=[self.project.id, proposal.id]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        proposal.refresh_from_db()
        self.assertEqual(proposal.document_date, date(2015, 7, 28))
        self.assertEqual(proposal.json['header'], 'new header')
        self.assertEqual(proposal.json['footer'], 'new footer')
        self.assertEqual(proposal.notes, 'new notes')

    def test_serialize_n_render_with_lineitems(self):
        self.project = ProjectFactory(structure="0.0")
        self.job = JobFactory(project=self.project)
        self.task = TaskFactory(qty=10, complete=5, price=96, group=self.job)
        self.lineitem = LineItemFactory(price=2, task=self.task)

        self.contact = ContactFactory(
            project=self.project,
            is_billable=True
        )

        data = self.form_data({
            'title': 'Proposal #1',
            'document_date': '2015-01-01',
            'header': 'hello',
            'footer': 'bye',
            'add_terms': False,
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'True'
        })
        response = self.client.post(reverse('proposal.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        # render

        response = self.client.get(reverse('proposal.pdf', kwargs={
            'project_pk':self.project.id,
            'pk': Proposal.objects.first().id,
            'format':'print',})+'?with_lineitems=1')
        extractedText = PdfFileReader(BytesIO(response.content)).getPage(0).extractText()
        for text in ['Proposal', 'hello', 'bye', self.job.name, self.task.name]:
            self.assertTrue(text in extractedText)
        extractedText = PdfFileReader(BytesIO(response.content)).getPage(1).extractText()
        for text in [self.task.name, self.task.lineitems.first().name]:
            self.assertTrue(text in extractedText)

    def test_serialize_n_render_only_groups(self):
        self.project = ProjectFactory(structure="0.0.0")
        self.job = JobFactory(project=self.project)
        self.group = GroupFactory(job=self.job, depth=1)
        self.task = TaskFactory(qty=10, complete=0, price=100, group=self.group)
        self.contact = ContactFactory(project=self.project, is_billable=True)

        data = self.form_data({
            'title': 'Proposal with only groups',
            'document_date': '2017-03-06',
            'header': 'hello',
            'footer': 'bye',
            'add_terms': False,
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'True'
        })

        response = self.client.post(reverse('proposal.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        # render

        response = self.client.get(reverse('proposal.pdf', kwargs={
            'project_pk':self.project.id,
            'pk': Proposal.objects.first().id,
            'format':'print',})+'?only_groups=1')
        extractedText = PdfFileReader(BytesIO(response.content)).getPage(0).extractText()
        for text in ['Proposal with only groups', 'hello', 'bye', self.job.name]:
            self.assertTrue(text in extractedText)
        for text in [self.task.name, self.task.description]:
            self.assertFalse(text in extractedText)


class EvidenceViewTests(DocumentTestCase):

    def test_generate_evidence(self):
        response = self.client.get(reverse('evidence.pdf', args=[
            self.project.id
        ]))
        self.assertEqual(200, response.status_code)


class LetterheadCreateTests(DocumentTestCase):

    def test_post(self):
        letterhead_count = Letterhead.objects.count()
        with open('systori/apps/document/test_data/letterhead.pdf', 'rb') as lettehead_pdf:
            response = self.client.post(
                reverse('letterhead.create'),
                {
                    'document_unit': Letterhead.mm,
                    'top_margin': 10,
                    'right_margin': 10,
                    'bottom_margin': 10,
                    'left_margin': 10,
                    'letterhead_pdf': lettehead_pdf,
                    'document_format': Letterhead.A4,
                    'orientation': Letterhead.PORTRAIT
                }
            )
        self.assertEqual(Letterhead.objects.count(), letterhead_count + 1)
        self.assertRedirects(response, reverse('letterhead.update', args=[Letterhead.objects.latest('pk').pk]))


class InvoiceListViewTest(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.worker.is_owner = True
        self.worker.save()
        project = ProjectFactory()
        InvoiceFactory(project=project, letterhead=LetterheadFactory())

    def test_kwarg_queryset_filter(self):
        response = self.client.get(reverse('invoice.list'))
        self.assertEqual(response.status_code, 200, response.content)

        response = self.client.get(reverse('invoice.list', kwargs={'status_filter': 'sent'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('invoice.list', kwargs={'status_filter': 'paid'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('invoice.list', kwargs={'status_filter': 'draft'}))
        self.assertEqual(response.status_code, 200)


@freeze_time('2017-04-10 18:30')
class TimesheetViewTests(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.letterhead = LetterheadFactory(with_settings=True)

    def create_january_timesheet(self):
        january = datetime(2017, 1, 9, 9)
        Timer.objects.create(
            worker=self.worker,
            started=january.replace(tzinfo=timezone.utc),
            stopped=january.replace(hour=18, tzinfo=timezone.utc),
            kind=Timer.WORK
        )
        Timer.objects.create(
            worker=self.worker,
            started=january.replace(day=10, tzinfo=timezone.utc),
            stopped=january.replace(day=10, hour=17, tzinfo=timezone.utc),
            kind=Timer.VACATION
        )
        return self.client.get(reverse('timesheets.generate', args=[2017, 1]))

    def test_generate_timesheet(self):
        self.assertEqual(Timesheet.objects.count(), 0)
        response = self.create_january_timesheet()
        self.assertEqual(response.status_code, 302)
        sheet = Timesheet.objects.get()
        self.assertEqual(sheet.json['first_weekday'], 6)
        self.assertEqual(sheet.json['work'][8], 9*60)
        self.assertEqual(sheet.json['work'][9], 0)
        self.assertEqual(sheet.json['overtime'][8], 60)
        self.assertEqual(sheet.json['overtime'][9], 0)
        self.assertEqual(sheet.json['overtime_total'], 60)
        self.assertEqual(sheet.json['overtime_transferred'], 0)
        self.assertEqual(sheet.json['overtime_balance'], 60)
        self.assertEqual(sheet.json['vacation'][8], 0)
        self.assertEqual(sheet.json['vacation'][9], 8*60)
        self.assertEqual(sheet.json['vacation_total'], 8*60)
        self.assertEqual(sheet.json['vacation_transferred'], 0)
        self.assertEqual(sheet.json['vacation_added'], 2.5*8*60)
        self.assertEqual(sheet.json['vacation_balance'], 12*60)
        self.assertEqual(sheet.json['compensation'][8], 8*60)
        self.assertEqual(sheet.json['compensation'][9], 8*60)
        self.assertEqual(sheet.json['compensation_total'], 16*60)

    def test_timesheet_transferred_totals(self):
        self.create_january_timesheet()
        february = datetime(2017, 2, 6, 9, tzinfo=timezone.utc)
        Timer.objects.create(
            worker=self.worker,
            started=february,
            stopped=february.replace(hour=18),
            kind=Timer.WORK
        )
        self.client.get(reverse('timesheets.generate', args=[2017, 2]))
        self.assertEqual(Timesheet.objects.count(), 2)
        sheet = Timesheet.objects.get(pk=2)
        self.assertEqual(sheet.json['overtime_transferred'], 60)
        self.assertEqual(sheet.json['overtime_total'], 60)
        self.assertEqual(sheet.json['overtime_balance'], 2*60)
        self.assertEqual(sheet.json['vacation_transferred'], 12*60)
        self.assertEqual(sheet.json['vacation_added'], 2.5*8*60)
        self.assertEqual(sheet.json['vacation_total'], 0)
        self.assertEqual(sheet.json['vacation_balance'], 32*60)

    def test_correction(self):
        self.create_january_timesheet()
        sheet = Timesheet.objects.get()
        self.client.post(reverse('timesheet.update', args=[sheet.pk]), data={
            'overtime_correction': 5.5,
            'overtime_correction_notes': 'added 5.5',
            'vacation_correction': 6.5,
            'vacation_correction_notes': 'added 6.5',
            'work_correction': 7.5,
            'work_correction_notes': 'added 7.5',
        })
        sheet.refresh_from_db()
        self.assertEqual(sheet.json['overtime_correction'], 5.5*60)
        self.assertEqual(sheet.json['overtime_correction_notes'], 'added 5.5')
        self.assertEqual(sheet.json['vacation_correction'], 6.5*60)
        self.assertEqual(sheet.json['vacation_correction_notes'], 'added 6.5')
        self.assertEqual(sheet.json['work_correction'], 7.5*60)
        self.assertEqual(sheet.json['work_correction_notes'], 'added 7.5')
        # regenerating does not wipe out the corrections, reusing previous timesheet
        self.client.get(reverse('timesheets.generate', args=[2017, 1]))
        sheet2 = Timesheet.objects.get()
        self.assertEqual(sheet.pk, sheet2.pk)
        self.assertEqual(sheet2.json['overtime_correction'], 5.5*60)
        self.assertEqual(sheet2.json['overtime_correction_notes'], 'added 5.5')
        self.assertEqual(sheet2.json['vacation_correction'], 6.5*60)
        self.assertEqual(sheet2.json['vacation_correction_notes'], 'added 6.5')
        self.assertEqual(sheet2.json['work_correction'], 7.5*60)
        self.assertEqual(sheet2.json['work_correction_notes'], 'added 7.5')
