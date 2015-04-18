from datetime import date
from django.utils.translation import ugettext_lazy as _
from django.forms import Form, ModelForm
from django import forms
from .models import *


class PaymentForm(Form):
    bank_account = forms.ModelChoiceField(label=_('Bank Account'), queryset=Account.objects.banks())
    amount = forms.DecimalField(label=_("Amount"), max_digits=14, decimal_places=4)
    received_on = forms.DateField(label=_("Received Date"), initial=date.today)
    is_discounted = forms.BooleanField(label=_('Is discounted?'), initial=False, required=False)


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name']