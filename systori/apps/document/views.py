from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Table, TableStyle, Frame, PageTemplate, FrameBreak


from ..project.models import Project
from ..task.models import Job
from .models import Proposal, Invoice, DocumentTemplate
from .forms import ProposalForm, InvoiceForm
from ..accounting import skr03

from .type import proposal, invoice, evidence


class DocumentRenderView(SingleObjectMixin, View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.pdf(), content_type='application/pdf')

    def pdf(self):
        raise NotImplementedError


# Proposal


class ProposalView(DetailView):
    model = Proposal


class ProposalPDF(DocumentRenderView):
    model = Proposal

    def pdf(self):
        json = self.get_object().json
        return proposal.render(json)


class ProposalCreate(CreateView):
    model = Proposal
    form_class = ProposalForm

    def get_form_kwargs(self):
        kwargs = super(ProposalCreate, self).get_form_kwargs()
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

        return super(ProposalCreate, self).form_valid(form)

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


class InvoicePDF(DocumentRenderView):
    model = Invoice

    def pdf(self):
        json = self.get_object().json
        return invoice.render(json)


class InvoiceCreate(CreateView):
    model = Invoice
    form_class = InvoiceForm

    def get_form_kwargs(self):
        kwargs = super(InvoiceCreate, self).get_form_kwargs()
        kwargs['instance'] = self.model(project=self.request.project)
        return kwargs

    def form_valid(self, form):

        project = Project.prefetch(self.request.project.id)

        # update account balance with any new work that's been done
        if project.new_amount_to_debit:
            skr03.partial_debit(project)

        form.instance.amount = project.account.balance
        form.instance.json = invoice.serialize(project, form)
        form.instance.json_version = form.instance.json['version']

        return super(InvoiceCreate, self).form_valid(form)

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
    fields = '__all__'
    success_url = reverse_lazy('templates')


class DocumentTemplateUpdate(UpdateView):
    model = DocumentTemplate
    fields = '__all__'
    success_url = reverse_lazy('templates')


class DocumentTemplateDelete(DeleteView):
    model = DocumentTemplate
    success_url = reverse_lazy('templates')

