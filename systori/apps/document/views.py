from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy

from .models import Proposal, Invoice, Evidence, DocumentTemplate
from .forms import ProposalForm, InvoiceForm, EvidenceForm
from ..accounting import skr03
from ..accounting.models import *


class BaseDocumentPDFView(SingleObjectMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        pdf = getattr(self.object, kwargs['format']+'_pdf')
        return HttpResponse(pdf, content_type='application/pdf')


# Proposal


class ProposalView(DetailView):
    model = Proposal


class ProposalPDF(BaseDocumentPDFView):
    model = Proposal


class ProposalCreate(CreateView):
    model = Proposal
    form_class = ProposalForm

    def get_form_kwargs(self):
        kwargs = super(ProposalCreate, self).get_form_kwargs()
        kwargs['instance'] = self.model(project=self.request.project)
        return kwargs

    def form_valid(self, form):

        amount = Decimal(0.0)
        for job in form.cleaned_data['jobs']:
            job.status = job.PROPOSED
            job.save()
            amount += job.estimate_total
        form.instance.amount = amount

        redirect = super(ProposalCreate, self).form_valid(form)

        self.object.generate_document(form.cleaned_data['add_terms'])

        return redirect

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class ProposalTransition(SingleObjectMixin, View):
    model = Proposal

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        transition = None
        for t in self.object.get_available_status_transitions():
            if t.name == kwargs['transition']:
                transition = t
                break

        if transition:
            getattr(self.object, transition.name)()
            self.object.save()

        return HttpResponseRedirect(reverse('project.view',
                                            args=[self.object.project.id]))

class ProposalDelete(DeleteView):
    model = Proposal

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


# Invoice


class InvoiceView(DetailView):
    model = Invoice


class InvoicePDF(BaseDocumentPDFView):
    model = Invoice


class InvoiceCreate(CreateView):
    model = Invoice
    form_class = InvoiceForm

    def get_form_kwargs(self):
        kwargs = super(InvoiceCreate, self).get_form_kwargs()
        kwargs['instance'] = self.model(project=self.request.project)
        return kwargs

    def form_valid(self, form):

        project = self.request.project

        # update account balance with any new work that's been done
        if skr03.new_amount_to_debit(project):
            group = TransactionGroup.objects.create()
            skr03.partial_debit(group, project)

        # record account balance in document record
        form.instance.amount = project.account.balance

        redirect = super(InvoiceCreate, self).form_valid(form)

        self.object.generate_document(form.cleaned_data['add_terms'])

        return redirect

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class InvoiceTransition(SingleObjectMixin, View):
    model = Invoice

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        transition = None
        for t in self.object.get_available_status_transitions():
            if t.name == kwargs['transition']:
                transition = t
                break

        if transition:
            getattr(self.object, transition.name)()
            self.object.save()

        return HttpResponseRedirect(reverse('project.view',
                                            args=[self.object.project.id]))


class InvoiceDelete(DeleteView):
    model = Invoice

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


# Document Template


class DocumentTemplateView(DetailView):
    model = DocumentTemplate


class DocumentTemplateCreate(CreateView):
    model = DocumentTemplate
    success_url = reverse_lazy('templates')


class DocumentTemplateUpdate(UpdateView):
    model = DocumentTemplate
    success_url = reverse_lazy('templates')


class DocumentTemplateDelete(DeleteView):
    model = DocumentTemplate
    success_url = reverse_lazy('templates')


# Evidence


class EvidenceDocumentCreateView(CreateView):

    def get_form_kwargs(self):
        kwargs = super(EvidenceDocumentCreateView, self).get_form_kwargs()
        kwargs['instance'] = self.model(project=self.request.project)
        return kwargs

    def form_valid(self, form):

        redirect = super(EvidenceDocumentCreateView, self).form_valid(form)
        self.object.generate_document(form.cleaned_data)

        return redirect

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class EvidenceView(DetailView):
    model = Evidence


class EvidencePDF(BaseDocumentPDFView):
    model = Evidence


class EvidenceCreate(EvidenceDocumentCreateView):
    model = Evidence
    form_class = EvidenceForm

    def process_job(self, job):
        return job.billable_total


class EvidenceDelete(DeleteView):
    model = Evidence

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])
