from django.forms import ModelForm
from django import forms
from .models import Payment


class PaymentForm(ModelForm):

    class Meta:
        model = Payment
        fields = ['amount', 'date_sent', 'date_received', 'is_discounted']