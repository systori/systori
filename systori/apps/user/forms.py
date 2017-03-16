from decimal import Decimal

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm

from systori.lib.fields import DecimalMinuteHoursField
from ..company.models import Worker, Contract
from .models import *


class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    email = forms.EmailField(required=False)
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, required=False,
                                help_text=_("Enter the same password as above, for verification."))

    def clean_email(self):
        if not self.cleaned_data['email']:
            return None
        return self.cleaned_data['email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('first_name') and\
           not cleaned_data.get('last_name') and\
           not cleaned_data.get('email'):
            raise forms.ValidationError(_('A name or email is required.'))

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class AuthenticationForm(BaseAuthenticationForm):
    username = forms.CharField(max_length=254, initial='')


class WorkerForm(ModelForm):
    
    class Meta:
        model = Worker
        exclude = ['company', 'user', 'contract']


class ContractForm(ModelForm):

    class Meta:
        model = Contract
        exclude = ['name', 'is_template', 'worker']
        localized_fields = ['rate', 'vacation', 'abandoned_timer_penalty']
        field_classes = {
            'vacation': DecimalMinuteHoursField,
            'abandoned_timer_penalty': DecimalMinuteHoursField,
        }


class LanguageForm(ModelForm):

    class Meta:
        model = User
        fields = ['language']
