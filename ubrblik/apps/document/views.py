import os.path, shutil
from subprocess import Popen, PIPE
from tempfile import TemporaryDirectory

from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.loader import get_template
from django.template import Context

from .models import Proposal, Invoice
from .forms import ProposalForm, InvoiceForm


class ProposalView(DetailView):
    model = Proposal


class ProposalCreate(CreateView):
    model = Proposal
    form_class = ProposalForm

    def get_form_kwargs(self):
        kwargs = super(ProposalCreate, self).get_form_kwargs()
        kwargs['instance'] = Proposal(project=self.request.project)
        return kwargs

    def form_valid(self, form):
        amount = Decimal(0.0)
        for job in form.cleaned_data['jobs']:
            amount += job.estimate_total
            job.status = job.PROPOSED
            job.save()
        form.instance.amount = amount
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

        return HttpResponseRedirect(reverse('project.view', args=[self.object.project.id]))


class ProposalDelete(DeleteView):
    model = Proposal
    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class InvoiceView(DetailView):
    model = Invoice


class InvoiceCreate(CreateView):
    model = Invoice
    form_class = InvoiceForm

    def get_form_kwargs(self):
        kwargs = super(InvoiceCreate, self).get_form_kwargs()
        kwargs['instance'] = Invoice(project=self.request.project)
        return kwargs

    def form_valid(self, form):
        amount = Decimal(0.0)
        for job in form.cleaned_data['jobs']:
            amount += job.billable_total
        form.instance.amount = amount
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

        return HttpResponseRedirect(reverse('project.view', args=[self.object.project.id]))


class InvoiceDelete(DeleteView):
    model = Invoice
    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])