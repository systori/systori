from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy

from ..project.models import Project
from ..task.models import Job
from .models import Proposal, Invoice, DocumentTemplate
from .forms import ProposalForm, InvoiceForm, ProposalUpdateForm, InvoiceUpdateForm
from ..accounting import skr03

from .type import proposal, invoice, evidence, specification, itemized_listing


class DocumentRenderView(SingleObjectMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.pdf(), content_type='application/pdf')

    def pdf(self):
        raise NotImplementedError


# Specification


class SpecificationPDF(DocumentRenderView):
    model = Proposal

    def pdf(self):
        json = self.get_object().json
        return specification.render(json, self.kwargs['format'])

# Proposal


class ProposalView(DetailView):
    model = Proposal


class ProposalPDF(DocumentRenderView):
    model = Proposal

    def pdf(self):
        json = self.get_object().json
        return proposal.render(json, self.request.GET.get('with_lineitems', False), self.kwargs['format'])


class ProposalCreate(CreateView):
    form_class = ProposalForm
    model = Proposal

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.model(project=self.request.project)
        return kwargs

    def form_valid(self, form):
        form.cleaned_data['jobs'] = [
            Job.prefetch(job.id) for job in form.cleaned_data['jobs']
            ]

        amount = Decimal(0.0)
        for job in form.cleaned_data['jobs']:
            amount += job.estimate_total

        form.instance.amount = amount
        form.instance.json = proposal.serialize(self.request.project, form)
        form.instance.json_version = form.instance.json['version']

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class ProposalUpdate(UpdateView):
    form_class = ProposalUpdateForm
    model = Proposal

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = self.object.json
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(project=self.request.project)

    def form_valid(self, form):
        proposal.update(self.object, form.cleaned_data)
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


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


# Invoice


class InvoiceView(DetailView):
    model = Invoice


class InvoicePDF(DocumentRenderView):
    model = Invoice

    def pdf(self):
        json = self.get_object().json
        return invoice.render(json, self.kwargs['format'])


class InvoiceCreate(CreateView):
    model = Invoice
    form_class = InvoiceForm

    def get_form_kwargs(self):
        kwargs = super(InvoiceCreate, self).get_form_kwargs()
        kwargs['instance'] = self.model(project=self.request.project)
        return kwargs

    def form_valid(self, form):
        project = Project.prefetch(self.request.project.id)

        if form.cleaned_data['is_final']:
            skr03.final_debit(project)
            project.begin_settlement()
            project.save()

        elif project.new_amount_to_debit:
            # update account balance with any new work that's been done
            skr03.partial_debit(project)

        form.instance.amount = project.account.balance
        form.instance.json = invoice.serialize(project, form.cleaned_data)
        form.instance.json_version = form.instance.json['version']

        return super(InvoiceCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class InvoiceUpdate(UpdateView):
    model = Invoice
    form_class = InvoiceUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = self.object.json
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(project=self.request.project)

    def form_valid(self, form):
        invoice.update(self.object, form.cleaned_data)
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


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

        return HttpResponseRedirect(reverse('project.view',
                                            args=[doc.project.id]))


class InvoiceDelete(DeleteView):
    model = Invoice

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


# Evidence


class EvidencePDF(DocumentRenderView):
    model = Project

    def pdf(self):
        project = Project.prefetch(self.kwargs['project_pk'])
        return evidence.render(project)


# Itemized List

class ItemizedListingPDF(DocumentRenderView):
    model = Project

    def pdf(self):
        project = Project.prefetch(self.kwargs['project_pk'])
        return itemized_listing.render(project, self.kwargs['format'])

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
