from django.forms import ModelForm
from .models import Proposal, Invoice
from ..task.models import Job

class ProposalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_proposal

    class Meta:
        model = Proposal
        fields = ['notes', 'jobs']

class InvoiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_invoice

    class Meta:
        model = Invoice
        fields = ['notes', 'jobs']