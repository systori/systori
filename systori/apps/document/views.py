from datetime import date
from calendar import monthrange
from collections import OrderedDict, namedtuple
from itertools import chain

from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.views.generic import View, ListView, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import DateField

from systori.lib.accounting.tools import Amount
from ..project.models import Project
from ..timetracking.models import Timer
from ..accounting.constants import TAX_RATE
from .models import Proposal, Invoice, Adjustment, Payment, Refund, Timesheet
from .models import DocumentTemplate, Letterhead, DocumentSettings
from .forms import ProposalForm, InvoiceForm, AdjustmentForm, PaymentForm, RefundForm
from .forms import LetterheadCreateForm, LetterheadUpdateForm, DocumentSettingsForm
from .forms import TimesheetForm
from .utils import get_weekday_names_numbers_and_mondays
from . import type as pdf_type


class BaseDocumentViewMixin:

    def get_form_kwargs(self):
        kwargs = {
            'jobs': self.request.project.jobs.prefetch_related(
                'account'
            )
        }

        if not self.object:
            self.object = self.model(project=self.request.project)
            self.object.json['jobs'] = []

        kwargs['instance'] = self.object

        kwargs['initial'] = {}
        for field in self.form_class._meta.fields:
            if field in self.object.json:
                form_field = self.form_class.base_fields[field]
                if isinstance(form_field, DateField):
                    kwargs['initial'][field] = form_field.clean(self.object.json[field])
                else:
                    kwargs['initial'][field] = self.object.json[field]

        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST.copy()

        return kwargs

    def get_success_url(self):
        return self.request.project.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TAX_RATE'] = TAX_RATE
        return context

    def get_form(self):
        # document forms are very expensive to create
        if not hasattr(self, '_cached_form'):
            self._cached_form = super().get_form()
        return self._cached_form


class AccountingDocumentViewMixin(BaseDocumentViewMixin):

    def get_queryset(self):
        return self.model.objects.prefetch_related('transaction').all()


class DeleteViewMixin(DeleteView):

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class InvoiceViewMixin(AccountingDocumentViewMixin):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'accounting/invoice_form.html'


class InvoiceCreate(InvoiceViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'previous_pk' in self.kwargs:
            previous = Invoice.objects.get(id=self.kwargs['previous_pk'])
            self.object.parent = previous.parent if previous.parent else previous
            # copy basic values from previous invoice
            for field in ['title', 'header', 'footer', 'add_terms', 'vesting_start', 'vesting_end']:
                kwargs['initial'][field] = previous.json[field]
            # copy the list of jobs
            self.object.json['jobs'] = [{
                                            'job.id': debit['job.id'],
                                            'is_invoiced': True
                                        } for debit in previous.json['jobs']]
        return kwargs


class InvoiceUpdate(InvoiceViewMixin, UpdateView):
    pass


class InvoiceTransition(SingleObjectMixin, View):
    model = Invoice

    def get(self, request, *args, **kwargs):
        doc = self.get_object()

        transition = None
        for t in doc.get_available_status_transitions():
            if t.name == kwargs['transition']:
                transition = t
                break

        if transition:
            getattr(doc, transition.name)()
            doc.save()

        return HttpResponseRedirect(reverse('project.view', args=[doc.project.id]))


class InvoiceDelete(DeleteViewMixin):
    model = Invoice
    template_name = 'accounting/invoice_confirm_delete.html'


class AdjustmentViewMixin(AccountingDocumentViewMixin):
    model = Adjustment
    form_class = AdjustmentForm
    template_name = 'accounting/adjustment_form.html'


class AdjustmentCreate(AdjustmentViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'invoice_pk' in self.kwargs:
            invoice = Invoice.objects.get(id=self.kwargs['invoice_pk'])
            self.object.invoice = invoice
            kwargs['instance'].json['jobs'] = [{
                                                   'job.id': job['job.id'],
                                                   'invoiced': job['debit'],
                                                   'corrected': job['debit']
                                               } for job in invoice.json['jobs']
                                               ]
        return kwargs


class AdjustmentUpdate(AdjustmentViewMixin, UpdateView):
    pass


class AdjustmentDelete(DeleteViewMixin):
    model = Adjustment
    template_name = 'accounting/adjustment_confirm_delete.html'


class PaymentViewMixin(AccountingDocumentViewMixin):
    model = Payment
    form_class = PaymentForm
    template_name = 'accounting/payment_form.html'


class PaymentCreate(PaymentViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'invoice_pk' in self.kwargs:
            invoice = Invoice.objects.get(id=self.kwargs['invoice_pk'])
            self.object.invoice = invoice
            kwargs['initial'].update({
                'payment': invoice.json.get('corrected', invoice.json['debit']).gross,
            })
            kwargs['instance'].json['jobs'] = [{
                                                   'job.id': job['job.id'],
                                                   'invoiced': job.get('corrected', job['debit']),
                                                   'split': job.get('corrected', job['debit'])
                                               } for job in invoice.json['jobs']]
        return kwargs


class PaymentUpdate(PaymentViewMixin, UpdateView):
    pass


class PaymentDelete(DeleteViewMixin):
    model = Payment
    template_name = 'accounting/payment_confirm_delete.html'


class RefundViewMixin(AccountingDocumentViewMixin):
    model = Refund
    form_class = RefundForm
    template_name = 'accounting/refund_form.html'


class RefundCreate(RefundViewMixin, CreateView):
    pass


class RefundUpdate(RefundViewMixin, UpdateView):
    pass


class RefundDelete(DeleteViewMixin):
    model = Refund
    template_name = 'accounting/refund_confirm_delete.html'


TimesheetMonth = namedtuple(
    'TimesheetMonth', (
        'date',
        'can_generate',
        'count',
        'timesheets'
    )
)


class TimesheetsList(TemplateView):
    template_name = 'document/timesheets_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        year, month = today.year, today.month
        months = []
        while month > 0:
            months.append(
                TimesheetMonth(
                    date(year, month, 1),
                    can_generate=(
                        (month == today.month or month == today.month-1) and
                        Timer.objects.month(year, month).exists()
                    ),
                    count=Timesheet.objects.period(year, month).count(),
                    timesheets=Timesheet.objects.period(year, month).all()
                )
            )
            month -= 1
        context['months'] = months
        return context


class TimesheetUpdate(UpdateView):
    model = Timesheet
    form_class = TimesheetForm
    template_name = 'document/timesheet.html'

    def get_initial(self):
        return {key: self.object.json[key] for key in Timesheet.initial.keys()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lookup = dict(Timer.KIND_CHOICES)
        lookup.update({
            'payables': _('Total'),
            'overtime': _('Overtime'),
            'compensation': _('Compensation'),
        })
        json = self.object.json
        context['daynames'], context['daynumbers'], context['mondays'] =\
            get_weekday_names_numbers_and_mondays(json['first_weekday'], json['total_days'], False)
        context['rows'] = [
            (t, lookup[t], json[t], json[t+'_total']) for t in [
                'work', 'vacation', 'sick', 'public_holiday',
                'paid_leave', 'unpaid_leave', 'payables',
                'overtime', 'compensation',
            ]
        ]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        saved = False
        if form.is_valid():
            form.save()
            saved = True
        return self.render_to_response(self.get_context_data(
            saved=saved, form=form
        ))


class TimesheetsGenerateView(View):

    def get(self, request, *args, **kwargs):
        year, month = int(kwargs['year']), int(kwargs['month'])
        doc_date = timezone.localdate()
        if (doc_date.year, doc_date.month) != (year, month):
            doc_date = date(year, month, monthrange(year, month)[1])
        Timesheet.generate(doc_date)
        return HttpResponseRedirect(reverse('timesheets'))


class InvoiceList(ListView):
    model = Invoice
    template_name = 'accounting/invoice_list.html'

    def get(self, request, *args, **kwargs):
        self.status_filter = self.kwargs.get('status_filter', 'all')
        return super().get(self, request, *args, **kwargs)

    def get_queryset(self, model=model):
        if self.status_filter == 'draft':
            return model.objects.filter(status='draft')
        elif self.status_filter == 'sent':
            return model.objects.filter(status='sent')
        elif self.status_filter == 'paid':
            return model.objects.filter(status='paid')
        else:
            return model.objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.status_filter

        query = self.get_queryset()
        query = query.\
            prefetch_related('project').\
            prefetch_related('parent').\
            filter(document_date__gte=date(2015, 9, 1)).\
            order_by('-document_date', 'invoice_no')

        months = OrderedDict()
        for invoice in query:
            doc_date = date(invoice.document_date.year, invoice.document_date.month, 1)
            month = months.setdefault(doc_date, {
                'invoices': [],
                'debit': Amount.zero()
            })
            month['debit'] += invoice.json['debit']
            month['invoices'].append(invoice)

        context['invoice_groups'] = months

        return context


class DocumentRenderView(SingleObjectMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.pdf(), content_type='application/pdf')

    def pdf(self):
        raise NotImplementedError


class TimesheetsListPDF(DocumentRenderView):
    def pdf(self):
        year, month = int(self.kwargs['year']), int(self.kwargs['month'])
        queryset = Timesheet.objects.period(year, month)
        letterhead = DocumentSettings.objects.first().timesheet_letterhead
        return pdf_type.timesheet.render(queryset, letterhead)


class TimesheetPDF(DocumentRenderView):
    model = Timesheet

    def pdf(self):
        letterhead = DocumentSettings.objects.first().timesheet_letterhead
        return pdf_type.timesheet.render([self.get_object()], letterhead)


class InvoicePDF(DocumentRenderView):
    model = Invoice

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        payment_details = self.request.GET.get('payment_details', False)
        return pdf_type.invoice.render(json, letterhead, payment_details, self.kwargs['format'])


class AdjustmentPDF(DocumentRenderView):
    model = Adjustment

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        return pdf_type.adjustment.render(json, letterhead, self.kwargs['format'])


class PaymentPDF(DocumentRenderView):
    model = Payment

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        return pdf_type.payment.render(json, letterhead, self.kwargs['format'])


class RefundPDF(DocumentRenderView):
    model = Refund

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        return pdf_type.refund.render(json, letterhead, self.kwargs['format'])


class ProposalPDF(DocumentRenderView):
    model = Proposal

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        with_lineitems = self.request.GET.get('with_lineitems', False)
        only_groups = self.request.GET.get('only_groups', False)
        only_task_names = self.request.GET.get('only_task_names', False)
        return pdf_type.proposal.render(
            json, letterhead, with_lineitems, only_groups, only_task_names, self.kwargs['format'])


class ProposalHTML(SingleObjectMixin, View):
    model = Proposal

    def get(self, request, *args, **kwargs):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        with_lineitems = self.request.GET.get('with_lineitems', False)
        only_groups = self.request.GET.get('only_groups', False)
        only_task_names = self.request.GET.get('only_task_names', False)
        return HttpResponse(''.join(chain(
            ('<style>', pdf_type.proposal.css_gen(letterhead), '</style>'),
            pdf_type.proposal.html_gen(
                json, letterhead, with_lineitems, only_groups, only_task_names)
            )
        ))


class ProposalViewMixin(BaseDocumentViewMixin):
    model = Proposal
    form_class = ProposalForm


class ProposalCreate(ProposalViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'].json['jobs'] = []
        previous_proposal = self.model.objects.filter(project=self.request.project).last()
        if previous_proposal:
            for field in ['title', 'header', 'footer', 'add_terms']:
                kwargs['initial'][field] = previous_proposal.json[field]
        return kwargs


class ProposalUpdate(ProposalViewMixin, UpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class ProposalTransition(SingleObjectMixin, View):
    model = Proposal

    def get(self, request, *args, **kwargs):
        doc = self.get_object()

        transition = None
        for t in doc.get_available_status_transitions():
            if t.name == kwargs['transition']:
                transition = t
                break

        if transition:
            getattr(doc, transition.name)()
            doc.save()

        return HttpResponseRedirect(reverse('project.view',
                                            args=[doc.project.id]))


class ProposalDelete(DeleteView):
    model = Proposal

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


# Evidence


class EvidencePDF(DocumentRenderView):
    model = Project

    def pdf(self):
        doc_settings = DocumentSettings.get_for_language(get_language())
        letterhead = doc_settings.evidence_letterhead
        return pdf_type.evidence.render(self.request.project, letterhead)


# Itemized List


class ItemizedListingPDF(DocumentRenderView):
    model = Project

    def pdf(self):
        doc_settings = DocumentSettings.get_for_language(get_language())
        letterhead = doc_settings.itemized_letterhead
        return pdf_type.itemized_listing.render(self.request.project, letterhead, self.kwargs['format'])


# Document Template


class DocumentTemplateView(DetailView):
    model = DocumentTemplate


class DocumentTemplateCreate(CreateView):
    model = DocumentTemplate
    fields = '__all__'
    success_url = reverse_lazy('templates')


class DocumentTemplateUpdate(UpdateView):
    model = DocumentTemplate
    fields = '__all__'
    success_url = reverse_lazy('templates')


class DocumentTemplateDelete(DeleteView):
    model = DocumentTemplate
    success_url = reverse_lazy('templates')


# Letterhead


class LetterheadCreate(CreateView):
    form_class = LetterheadCreateForm
    model = Letterhead

    def get_success_url(self):
        return reverse('letterhead.update', args=[self.object.id])


class LetterheadUpdate(UpdateView):
    model = Letterhead
    form_class = LetterheadUpdateForm

    def get_success_url(self):
        return reverse('letterhead.update', args=[self.object.id])


class LetterheadDelete(DeleteView):
    model = Letterhead
    success_url = reverse_lazy('templates')


class LetterheadPreview(DocumentRenderView):
    def pdf(self):
        return pdf_type.letterhead.render(letterhead=Letterhead.objects.get(id=self.kwargs.get('pk')))


# Document Settings


class DocumentSettingsCreate(CreateView):
    model = DocumentSettings
    form_class = DocumentSettingsForm
    success_url = reverse_lazy('templates')


class DocumentSettingsUpdate(UpdateView):
    model = DocumentSettings
    form_class = DocumentSettingsForm
    success_url = reverse_lazy('templates')


class DocumentSettingsDelete(DeleteView):
    model = DocumentSettings
    success_url = reverse_lazy('templates')
