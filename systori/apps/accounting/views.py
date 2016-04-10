from django.views.generic import View, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy

from .forms import *
from .models import *


class EditViewMixin:

    def get_queryset(self):
        return self.model.objects.prefetch_related('transaction').all()

    def get_form(self):
        # document forms are very expensive to create
        if not hasattr(self, '_cached_form'):
            self._cached_form = super().get_form()
        return self._cached_form

    def get_form_kwargs(self):

        kwargs = {
            'jobs': self.request.project.jobs.prefetch_related(
                'taskgroups__tasks__taskinstances__lineitems',
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
                kwargs['initial'][field] = self.object.json[field]

        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST.copy()

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TAX_RATE'] = TAX_RATE
        return context

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
        if 'previous_pk' in self.kwargs:
            previous = Invoice.objects.get(id=self.kwargs['previous_pk'])
            self.object.parent = previous.parent if previous.parent else previous
            # copy basic values from previous invoice
            for field in ['title', 'header', 'footer', 'add_terms']:
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


class AdjustmentViewMixin(EditViewMixin):
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


class PaymentViewMixin(EditViewMixin):
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


class RefundViewMixin(EditViewMixin):
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


class AccountList(TemplateView):
    template_name = 'accounting/account_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banks'] = Account.objects.banks()
        context['other'] = Account.objects.exclude(account_type=Account.ASSET)
        return context


class AccountView(DetailView):
    model = Account


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
