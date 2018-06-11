from django.views.generic import TemplateView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from .forms import AccountForm, BankAccountForm
from .models import Account, Transaction


class AccountList(TemplateView):
    template_name = "accounting/account_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["banks"] = Account.objects.banks()
        context["other"] = Account.objects.exclude(account_type=Account.ASSET)
        return context


class AccountView(SingleObjectMixin, ListView):
    paginate_by = 10
    template_name = "accounting/account_detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Account.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account"] = self.object
        return context

    def get_queryset(self):
        return (
            Transaction.objects.prefetch_related("entries__account")
            .prefetch_related("entries__job__project")
            .filter(entries__account=self.object)
            .order_by("-transacted_on")
            .distinct()
        )


class AccountUpdate(UpdateView):
    model = Account
    form_class = AccountForm

    def get_success_url(self):
        return reverse("accounts")


class BankAccountCreate(CreateView):
    model = Account
    form_class = BankAccountForm

    def get_success_url(self):
        return reverse("accounts")


class BankAccountUpdate(UpdateView):
    model = Account
    form_class = BankAccountForm

    def get_success_url(self):
        return reverse("accounts")


class BankAccountDelete(DeleteView):
    model = Account
    success_url = reverse_lazy("accounts")
