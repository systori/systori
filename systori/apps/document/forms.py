from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets

from .models import Proposal, Invoice, DocumentTemplate, Letterhead
from .letterhead_utils import clean_letterhead_pdf


class ProposalForm(forms.ModelForm):
    doc_template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.filter(
            document_type=DocumentTemplate.PROPOSAL), required=False)
    add_terms = forms.BooleanField(label=_('Add Terms'),
                                   initial=True, required=False)
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)


    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_proposal

    class Meta:
        model = Proposal
        fields = ['doc_template', 'document_date', 'header', 'footer',
                  'jobs', 'add_terms', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }


class ProposalUpdateForm(forms.ModelForm):
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Proposal
        fields = ['document_date', 'header', 'footer', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }


class InvoiceForm(forms.ModelForm):
    doc_template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.filter(
            document_type=DocumentTemplate.INVOICE), required=False)
    add_terms = forms.BooleanField(label=_('Add Terms'), initial=True, required=False)
    is_final = forms.BooleanField(label=_('Is Final Invoice?'), initial=False, required=False)

    title = forms.CharField(label=_('Title'), initial=_("Invoice"))
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = ['doc_template', 'is_final', 'document_date', 'invoice_no', 'title', 'header', 'footer', 'add_terms', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }


class InvoiceUpdateForm(forms.ModelForm):
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Invoice
        fields = ['document_date', 'header', 'footer', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }


class LetterheadCreateForm(forms.ModelForm):

    def clean(self):
        clean_letterhead_pdf(self.cleaned_data.get('letterhead_pdf'))

    def save(self):
        return clean_letterhead_pdf(self.cleaned_data.get('letterhead_pdf'), save=True)

    class Meta:
        model = Letterhead
        fields = ['letterhead_pdf']


class LetterheadUpdateForm(forms.ModelForm):
    class Meta:
        model = Letterhead
        exclude = []
