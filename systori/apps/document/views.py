from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy

from ..project.models import Project
from ..task.models import Job
from .models import Proposal, Invoice, DocumentTemplate, Letterhead, DocumentSettings
from .forms import ProposalForm, ProposalUpdateForm, LetterheadCreateForm, LetterheadUpdateForm, DocumentSettingsForm
from ..accounting.forms import InvoiceForm
from .type import proposal, invoice, evidence, letterhead, itemized_listing


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
        letterhead = self.get_object().letterhead
        return proposal.render(json, letterhead, self.request.GET.get('with_lineitems', False), self.kwargs['format'])


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

        data = form.cleaned_data
        data['amount'] = amount

        form.instance.letterhead = Letterhead.objects.first()
        form.instance.json = proposal.serialize(self.request.project, data)

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
        letterhead = self.get_object().letterhead
        return invoice.render(json, letterhead, self.kwargs['format'])


class InvoiceFormMixin:
    model = Invoice
    form_class = InvoiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PERCENT_RANGE'] = [5, 20, 25, 30, 50, 75, 100]
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
        return reverse('project.view', args=[self.request.project.id])


class InvoiceCreate(InvoiceFormMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = kwargs['instance']
        if 'previous_invoice_id' in self.request.GET:
            previous_id = int(self.request.GET['previous_invoice_id'])
            previous = Invoice.objects.get(id=previous_id)
            instance.parent = previous.parent if previous.parent else previous
            # copy all the basic stuff from previous invoice
            for field in ['title', 'header', 'footer', 'add_terms']:
                instance.json[field] = previous.json[field]
            # copy the list of jobs
            instance.json['debits'] = [
                {'job.id': debit['job.id'], 'is_booked': False}
                for debit in previous.json['debits']
            ]
        else:
            instance.json['debits'] = []
        return kwargs


class InvoiceUpdate(InvoiceFormMixin, UpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class InvoiceTransition(SingleObjectMixin, View):
    model = Invoice

    def get(self, request, *args, **kwargs):
        doc = self.get_object()

        transition = None
        for t in doc.get_available_status_transitions():
            if t.name == kwargs['transition']:
                transition = t
                break

        if transition.name == 'pay':
            return HttpResponseRedirect(reverse('payment.create', args=[doc.project.id, doc.id]))

        else:
            getattr(doc, transition.name)()
            doc.save()

        return HttpResponseRedirect(reverse('project.view', args=[doc.project.id]))


class InvoiceDelete(DeleteView):
    model = Invoice

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.object.transaction:
            self.object.transaction.delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


# Evidence


class EvidencePDF(DocumentRenderView):
    model = Project

    def pdf(self):
        project = Project.prefetch(self.kwargs['project_pk'])
        letterhead = DocumentSettings.objects.first().evidence_letterhead
        return evidence.render(project, letterhead)


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
        return letterhead.render(letterhead=Letterhead.objects.get(id=self.kwargs.get('pk')))


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

