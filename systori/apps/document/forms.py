from django import forms
from django.conf import settings
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from .models import Proposal, DocumentTemplate, Letterhead, DocumentSettings
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
        super().__init__(*args, **kwargs)
        self.fields['jobs'].queryset = self.instance.project.jobs_for_proposal
        default_text = DocumentSettings.get_for_language(settings.LANGUAGE_CODE)
        if default_text and default_text.proposal_text:
            rendered = default_text.proposal_text.render(self.instance.project)
            self.initial['header'] = rendered['header']
            self.initial['footer'] = rendered['footer']

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


class DocumentSettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proposal_text'].queryset = DocumentTemplate.objects.filter(document_type=DocumentTemplate.PROPOSAL)
        self.fields['invoice_text'].queryset = DocumentTemplate.objects.filter(document_type=DocumentTemplate.INVOICE)

    class Meta:
        model = DocumentSettings
        fields = '__all__'
