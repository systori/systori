from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .models import Proposal, Invoice, DocumentTemplate
from ..task.models import Job
from django.forms import widgets


class ProposalForm(forms.ModelForm):
    doc_template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.filter(
            document_type=DocumentTemplate.PROPOSAL), required=False)
    latex_template = forms.ChoiceField(choices = [(k,_(v)) for k,v in settings.PROPOSAL_LATEX_TEMPLATES])
    add_terms = forms.BooleanField(label=_('Add Terms'),
                                   initial=True, required=False)

    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_proposal

    class Meta:
        model = Proposal
        fields = ['doc_template', 'latex_template', 'document_date', 'header', 'footer',
                  'jobs', 'add_terms', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }


class InvoiceForm(forms.ModelForm):
    doc_template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.filter(
            document_type=DocumentTemplate.INVOICE), required=False)
    add_terms = forms.BooleanField(label=_('Add Terms'), initial=True,
                                   required=False)

    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = ['doc_template', 'document_date', 'invoice_no', 'header', 'footer', 'add_terms', 'notes']
        widgets = {
            'document_date': DateInput(attrs={'type': 'date'}),
        }


class EvidenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EvidenceForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs

    class Meta:
        model = Evidence
        fields = ['document_date', 'jobs']
        widgets = {
            'document_date': DateInput(attrs={'type': 'date'}),
        }
