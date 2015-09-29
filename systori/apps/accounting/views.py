from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from .models import *
from .forms import *
from .skr03 import *


class PaymentCreate(FormView):
    form_class = PaymentForm
    template_name = 'accounting/payment_form.html'

    def get_split_forms(self):
        return PaymentSplitFormSet(self.request.POST, jobs=self.request.project.jobs.all())

    def get(self, request, *args, **kwargs):
        return self.render_to_response(
            self.get_context_data(
                form=kwargs.get('form', self.get_form()),
                split=kwargs.get('split', self.get_split_forms()))
        )

    def post(self, request, *args, **kwargs):

        form = self.get_form()
        split_forms = self.get_split_forms()
        split_forms.set_payment_form(form)

        if form.is_valid() and split_forms.is_valid():

            split_forms.save()

            return HttpResponseRedirect(self.get_success_url())

        return self.get(form=form, split=split_forms)

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class TransactionDelete(DeleteView):
    model = Transaction

    def delete(self, request, *args, **kwargs):
        object = self.get_object()
        if not object.is_reconciled:
            object.delete()
        return HttpResponseRedirect(self.get_success_url())


class PaymentDelete(TransactionDelete):
    template_name = 'accounting/payment_confirm_delete.html'

    def get_success_url(self):
        return self.request.project.get_absolute_url()


class AccountList(TemplateView):
    template_name = 'accounting/account_list.html'

    def get_context_data(self, **kwargs):
        context = super(AccountList, self).get_context_data(**kwargs)
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
