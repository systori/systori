from django import forms
from .models import Proposal, Invoice
from ..document.models import DocumentTemplate
from ..task.models import Job
from django.forms.widgets import DateInput


class ProposalForm(forms.ModelForm):
    doc_template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.filter(
            document_type=DocumentTemplate.PROPOSAL), required=False)
    add_terms = forms.BooleanField(label='Add Terms',
                                   initial=True, required=False)

    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_proposal

    class Meta:
        model = Proposal
        fields = ['doc_template', 'document_date', 'header', 'footer',
                  'jobs', 'add_terms', 'notes']
        widgets = {
            'document_date': DateInput(attrs={'type': 'date'}),
        }


class InvoiceForm(forms.ModelForm):
    add_terms = forms.BooleanField(label='Add Terms', initial=True,
                                   required=False)

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_invoice

    class Meta:
        model = Invoice
        fields = ['document_date', 'header', 'footer',
                  'jobs', 'add_terms', 'notes']
        widgets = {
            'document_date': DateInput(attrs={'type': 'date'}),
        }
