from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django import forms
from .models import Payment


class PaymentForm(ModelForm):

    is_discounted = forms.BooleanField(label=_('Is discounted?'), initial=False, required=False)

    class Meta:
        model = Payment
        fields = ['amount', 'date_sent', 'date_received', 'is_discounted']