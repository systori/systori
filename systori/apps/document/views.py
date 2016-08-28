from datetime import date
from decimal import Decimal
from collections import OrderedDict

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic import View, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import get_language

from systori.lib.accounting.tools import Amount
from ..project.models import Project
from ..accounting.constants import TAX_RATE
from .models import Proposal, Invoice, Adjustment, Payment, Refund
from .models import DocumentTemplate, Letterhead, DocumentSettings
from .forms import ProposalForm, LetterheadCreateForm, LetterheadUpdateForm, DocumentSettingsForm
from . import type as pdf_type


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
        return pdf_type.proposal.render(json, letterhead, with_lineitems, self.kwargs['format'])


class ProposalViewMixin:
    model = Proposal
    form_class = ProposalForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TAX_RATE'] = TAX_RATE
        return context

    def get_form_kwargs(self):
        jobs = self.request.project.jobs.prefetch_related('taskgroups__tasks__taskinstances__lineitems').all()
        kwargs = {
            'jobs': jobs,
            'instance': self.model(project=self.request.project),
        }
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST.copy()
        return kwargs

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class ProposalCreate(ProposalViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'].json['jobs'] = []
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
        project = Project.prefetch(self.kwargs['project_pk'])
        doc_settings = DocumentSettings.get_for_language(get_language())
        letterhead = doc_settings.evidence_letterhead
        return pdf_type.evidence.render(project, letterhead)


# Itemized List

class ItemizedListingPDF(DocumentRenderView):
    model = Project

    def pdf(self):
        project = Project.prefetch(self.kwargs['project_pk'])
        return pdf_type.itemized_listing.render(project, self.kwargs['format'])

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


class LetterheadView(DetailView):
    model = Letterhead


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
