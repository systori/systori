from datetime import date
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.forms import Form, ModelForm, ValidationError
from django import forms
from systori.lib.fields import LocalizedDecimalField
from ..task.models import Job
from .skr03 import Account


class AccountSplitForm(Form):
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.all(), widget=forms.HiddenInput())
    amount = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=4)
    discount = forms.TypedChoiceField(
        label=_('Is discounted?'),
        coerce=Decimal,
        choices=[
            ('0', _('No discount applied')),
            ('0.03', _('3%')),
            ('0.1', _('10%')),
        ]
    )


class BaseAccountSplitFormSet(BaseFormSet):

    def __init__(self, payment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payment = payment

    def clean(self):
        splits = Decimal(0.0)
        for form in self.forms:
            splits += form.cleaned_data['amount']
        if splits != self.payment:
            raise forms.ValidationError(_("The sum of splits must equal the payment amount."))

AccountSplitFormSet = formset_factory(AccountSplitForm, formset=BaseAccountSplitFormSet, extra=0)


class PaymentForm(Form):
    bank_account = forms.ModelChoiceField(label=_("Bank Account"), queryset=Account.objects.banks())
    amount = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=4)
    received_on = forms.DateField(label=_("Received Date"), initial=date.today, localize=True)


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name']


class BankAccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name']

    def __init__(self, *args, instance=None, **kwargs):
        if instance is None:  # create form
            banks = Account.objects.banks().order_by('-code')
            if banks.exists():
                next_code = int(banks.first().code) + 1
            else:
                next_code = BANK_CODE_RANGE[0]

            if next_code <= BANK_CODE_RANGE[1]:
                # set initial only if we were able to compute code within range
                kwargs['initial'] = {'code': str(next_code)}

            kwargs['instance'] = Account(account_type=Account.ASSET)
        else:
            kwargs['instance'] = instance

        super(BankAccountForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']

        if not code.isdigit() or \
                        int(code) < BANK_CODE_RANGE[0] or \
                        int(code) > BANK_CODE_RANGE[1]:
            raise ValidationError(_("Account code must be a number between %(min)s and %(max)s inclusive."),
                                  code='invalid', params={'min': BANK_CODE_RANGE[0], 'max': BANK_CODE_RANGE[1]})

        return code
