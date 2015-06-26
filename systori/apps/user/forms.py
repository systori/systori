from django.forms import ModelForm
from .models import *


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',
                  'is_active', 'is_staff', 'is_foreman', 'is_laborer']
