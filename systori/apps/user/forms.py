from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from .models import *
from ..company.models import Access


class UserForm(ModelForm):

    email = forms.EmailField(required=False)

    def clean_email(self):
        if not self.cleaned_data['email']:
            return None
        return self.cleaned_data['email']

    def clean(self):
        if not self.cleaned_data['first_name'] and\
           not self.cleaned_data['last_name'] and\
           not self.cleaned_data['email']:
            raise forms.ValidationError(_('A name or email is required.'))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class AccessForm(ModelForm):

    class Meta:
        model = Access
        fields = ['is_active', 'is_staff', 'is_foreman', 'is_laborer']
