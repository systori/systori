from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy

from .models import Proposal, Invoice
from .forms import ProposalForm, InvoiceForm


class BaseDocumentPDFView(SingleObjectMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.pdf, content_type='application/pdf')

class BaseDocumentCreateView(CreateView):
    
    def get_form_kwargs(self):
        kwargs = super(BaseDocumentCreateView, self).get_form_kwargs()
        kwargs['instance'] = self.model(project=self.request.project)
        return kwargs

    def form_valid(self, form):

        amount = Decimal(0.0)
        for job in form.cleaned_data['jobs']:
            amount += self.process_job(job)
        form.instance.amount = amount

        redirect = super(BaseDocumentCreateView, self).form_valid(form)

        self.object.generate_document(form.cleaned_data['corporate_letterhead'])

        return redirect

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class ProposalView(DetailView):
    model = Proposal


class ProposalPDF(BaseDocumentPDFView):
    model = Proposal


class ProposalCreate(BaseDocumentCreateView):
    model = Proposal
    form_class = ProposalForm
    def process_job(self, job):
        job.status = job.PROPOSED
        job.save()
        return job.estimate_total


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

        return HttpResponseRedirect(reverse('project.view', args=[self.object.project.id]))


class ProposalDelete(DeleteView):
    model = Proposal
    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class InvoiceView(DetailView):
    model = Invoice

class InvoicePDF(BaseDocumentPDFView):
    model = Invoice

class InvoiceCreate(BaseDocumentCreateView):
    model = Invoice
    form_class = InvoiceForm
    def process_job(self, job):
        return job.billable_total


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

        return HttpResponseRedirect(reverse('project.view', args=[self.object.project.id]))


class InvoiceDelete(DeleteView):
    model = Invoice
    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


