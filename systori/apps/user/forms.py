from django import forms
from django.forms import ModelForm
from .models import *


class UserForm(ModelForm):

    email = forms.EmailField(required=False)

    def clean_email(self):
        if not self.cleaned_data['email']:
            return None
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',
                  'is_active', 'is_staff', 'is_foreman', 'is_laborer']
