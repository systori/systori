from django.views.generic import View, TemplateView, FormView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .models import *
from .forms import *


class InvoiceFormMixin:
    model = Invoice
    form_class = InvoiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TAX_RATE'] = TAX_RATE
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
        return self.request.project.get_absolute_url()


class InvoiceCreate(InvoiceFormMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = kwargs['instance']
        if 'previous_pk' in self.kwargs:
            previous = Invoice.objects.get(id=self.kwargs['previous_pk'])
            instance.parent = previous.parent if previous.parent else previous
            # copy all the basic stuff from previous invoice
            for field in ['title', 'header', 'footer', 'add_terms']:
                instance.json[field] = previous.json[field]
            # copy the list of jobs
            instance.json['jobs'] = [{
                'job.id': debit['job.id'],
                'is_invoiced': True
            } for debit in previous.json['jobs']]
        else:
            instance.json['jobs'] = []
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


class AdjustmentFormMixin:
    model = Adjustment
    form_class = AdjustmentForm
    template_name = 'accounting/adjustment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TAX_RATE'] = TAX_RATE
        return context

    def get_form_kwargs(self):
        jobs = self.request.project.jobs.prefetch_related('taskgroups__tasks__taskinstances__lineitems')
        kwargs = {
            'jobs': jobs,
            'instance': self.model(project=self.request.project),
        }
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST.copy()
        return kwargs

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class AdjustmentCreate(AdjustmentFormMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'invoice_pk' in self.kwargs:
            invoice = Invoice.objects.get(id=self.kwargs['invoice_pk'])
            kwargs['initial'] = {'invoice': invoice}
            kwargs['instance'].json['jobs'] = [
                {'job.id': debit['job.id'], 'approved': debit['amount']}
                for debit in invoice.json['debits']
                ]
        else:
            kwargs['instance'].json['jobs'] = []
        return kwargs


class AdjustmentDelete(DeleteView):
    model = Adjustment
    template_name = 'accounting/adjustment_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.object.transaction:
            self.object.transaction.delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class PaymentCreate(FormView):
    form_class = PaymentFormSet
    template_name = 'accounting/payment_form.html'

    def get_form_kwargs(self):
        kwargs = {'jobs': self.request.project.jobs.all()}
        if 'invoice_pk' in self.kwargs:
            invoice = Invoice.objects.get(id=self.kwargs['invoice_pk'])
            kwargs['initial'] = {
                'invoice': invoice,
                'amount': invoice.json['debit_gross'],
            }
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST.copy()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TAX_RATE'] = TAX_RATE
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class PaymentDelete(DeleteView):
    model = Transaction
    template_name = 'accounting/payment_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        object = self.get_object()
        if not object.is_reconciled:
            object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class RefundCreate(CreateView):
    form_class = RefundForm
    model = Refund

    def get_form_kwargs(self):
        kwargs = {
            'jobs': self.request.project.jobs.all(),
            'instance': self.model(project=self.request.project),
        }
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST.copy()
        return kwargs

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class RefundDelete(DeleteView):
    model = Refund

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.object.transaction:
            self.object.transaction.delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('project.view', args=[self.object.project.id])


class AccountList(TemplateView):
    template_name = 'accounting/account_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banks'] = Account.objects.banks()
        context['other'] = Account.objects.exclude(account_type=Account.ASSET)
        return context


class AccountView(DetailView):
    model = Account

    def get_queryset(self):
        queryset = super(AccountView, self).get_queryset()
        return queryset


class AccountUpdate(UpdateView):
    model = Account
    form_class = AccountForm

    def get_success_url(self):
        return reverse('accounts')


class BankAccountCreate(CreateView):
    model = Account
    form_class = BankAccountForm

    def get_success_url(self):
        return reverse('accounts')


class BankAccountUpdate(UpdateView):
    model = Account
    form_class = BankAccountForm

    def get_success_url(self):
        return reverse('accounts')


class BankAccountDelete(DeleteView):
    model = Account
    success_url = reverse_lazy('accounts')
