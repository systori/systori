from django import forms
from .models import Proposal, Invoice
from ..task.models import Job

class ProposalForm(forms.ModelForm):
    add_terms = forms.BooleanField(label='Add Terms', initial=True, required=False)
    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_proposal

    class Meta:
        model = Proposal
        fields = ['jobs', 'header', 'footer', 'add_terms', 'notes']

class InvoiceForm(forms.ModelForm):
    add_terms = forms.BooleanField(label='Add Terms', initial=True, required=False)
    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_invoice

    class Meta:
        model = Invoice
        fields = ['jobs', 'header', 'footer', 'add_terms', 'notes']