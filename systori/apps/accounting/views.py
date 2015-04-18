from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from .models import *
from .forms import *
from .skr03 import *

class PaymentCreate(FormView):
    form_class = PaymentForm
    template_name = 'accounting/payment_form.html'

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        is_discounted = form.cleaned_data['is_discounted']
        partial_credit([(self.request.project, amount, is_discounted)], amount)
        return super(PaymentCreate, self).form_valid(form)

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
        return queryset#.prefetch_related('jobs__taskgroups__tasks__taskinstances__lineitems')


class BankAccountCreate(CreateView):
    model = Account
    form_class = AccountForm

    def get_form_kwargs(self):
        kwargs = super(BankAccountCreate, self).get_form_kwargs()
        next_code = int(Account.objects.banks().order_by('-code').first().code)+1
        kwargs['instance'] = Account(account_type = Account.ASSET, code=str(next_code))
        return kwargs

    def get_success_url(self):
        return reverse('accounts')


class AccountUpdate(UpdateView):
    model = Account
    form_class = AccountForm

    def get_success_url(self):
        return reverse('accounts')


class BankAccountDelete(DeleteView):
    model = Account
    success_url = reverse_lazy('accounts')
