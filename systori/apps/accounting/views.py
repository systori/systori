from django.views.generic import View, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy

from .forms import *
from .models import *


class EditViewMixin:

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


class DeleteViewMixin(DeleteView):

    def delete(self, request, *args, **kwargs):
        doc = self.get_object()
        if doc.transaction:
            doc.transaction.delete()
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class InvoiceViewMixin(EditViewMixin):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'accounting/invoice_form.html'


class InvoiceCreate(InvoiceViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        initial = kwargs['initial'] = {}
        instance = kwargs['instance']
        if 'previous_pk' in self.kwargs:
            previous = Invoice.objects.get(id=self.kwargs['previous_pk'])
            instance.parent = previous.parent if previous.parent else previous
            # copy all the basic stuff from previous invoice
            for field in ['title', 'header', 'footer', 'add_terms']:
                initial[field] = previous.json[field]
            # copy the list of jobs
            instance.json['jobs'] = [{
                'job.id': debit['job.id'],
                'is_invoiced': True
            } for debit in previous.json['jobs']]
        else:
            instance.json['jobs'] = []
        return kwargs


class InvoiceUpdate(InvoiceViewMixin, UpdateView):
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

        if transition:
            getattr(doc, transition.name)()
            doc.save()

        return HttpResponseRedirect(reverse('project.view', args=[doc.project.id]))


class InvoiceDelete(DeleteViewMixin):
    model = Invoice
    template_name = 'accounting/invoice_confirm_delete.html'


class AdjustmentViewMixin(EditViewMixin):
    model = Adjustment
    form_class = AdjustmentForm
    template_name = 'accounting/adjustment_form.html'


class AdjustmentCreate(AdjustmentViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'invoice_pk' in self.kwargs:
            invoice = Invoice.objects.get(id=self.kwargs['invoice_pk'])
            kwargs['initial'] = {'invoice': invoice}
            kwargs['instance'].json['jobs'] = [{
                   'job.id': job['job.id'],
                   'invoiced': job['debit'],
                   'corrected': job['debit']
                } for job in invoice.json['jobs']
            ]
        else:
            kwargs['instance'].json['jobs'] = []
        return kwargs


class AdjustmentUpdate(AdjustmentViewMixin, UpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class AdjustmentDelete(DeleteViewMixin):
    model = Adjustment
    template_name = 'accounting/adjustment_confirm_delete.html'


class PaymentViewMixin(EditViewMixin):
    model = Payment
    form_class = PaymentForm
    template_name = 'accounting/payment_form.html'


class PaymentCreate(PaymentViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = kwargs['instance']
        if 'invoice_pk' in self.kwargs:
            invoice = Invoice.objects.get(id=self.kwargs['invoice_pk'])
            kwargs['initial'] = {
                'invoice': invoice,
                'payment': invoice.json.get('corrected', invoice.json['debit']).gross,
            }
            instance.json['jobs'] = [{
                'job.id': job['job.id'],
                'invoiced': job.get('corrected', job['debit']),
                'split': job.get('corrected', job['debit'])
            } for job in invoice.json['jobs']]
        else:
            instance.json['jobs'] = []
        return kwargs


class PaymentUpdate(PaymentViewMixin, UpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        kwargs['initial'] = {
            'bank_account': self.object.json['bank_account'],
            'payment': self.object.json['payment']
        }
        return kwargs


class PaymentDelete(DeleteViewMixin):
    model = Payment
    template_name = 'accounting/payment_confirm_delete.html'


class RefundViewMixin(EditViewMixin):
    model = Refund
    form_class = RefundForm
    template_name = 'accounting/refund_form.html'


class RefundCreate(RefundViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'].json['jobs'] = []
        return kwargs


class RefundUpdate(RefundViewMixin, UpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class RefundDelete(DeleteViewMixin):
    model = Refund
    template_name = 'accounting/refund_confirm_delete.html'


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
