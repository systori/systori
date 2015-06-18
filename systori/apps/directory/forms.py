from django.forms import ModelForm
from django.forms.models import modelform_factory
from .models import Contact, ProjectContact


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        exclude = ['projects']


class ProjectContactForm(ModelForm):
    class Meta:
        model = ProjectContact
        fields = ['association', 'is_billable']
