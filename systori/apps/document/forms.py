from django import forms
from django.conf import settings
from django.db.transaction import atomic
from django.forms import ValidationError
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from systori.lib.accounting.tools import Amount
from ..accounting.forms import DocumentForm, DocumentRowForm, BaseDocumentFormSet
from ..accounting.constants import TAX_RATE
from .models import Proposal, DocumentTemplate, Letterhead, DocumentSettings
from .letterhead_utils import clean_letterhead_pdf
from . import type as pdf_type


class ProposalForm(DocumentForm):

    doc_template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.filter(
            document_type=DocumentTemplate.PROPOSAL), required=False)

    add_terms = forms.BooleanField(label=_('Add Terms'), initial=True, required=False)

    title = forms.CharField(label=_('Title'), initial=_("Proposal"))
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    class Meta(DocumentForm.Meta):
        model = Proposal
        fields = ['doc_template', 'document_date', 'title', 'header', 'footer', 'add_terms', 'notes']

    def __init__(self, *args, jobs, **kwargs):
        super().__init__(*args, formset_class=ProposalFormSet, jobs=jobs, **kwargs)
        default_text = DocumentSettings.get_for_language(settings.LANGUAGE_CODE)
        if default_text and default_text.proposal_text:
            rendered = default_text.proposal_text.render(self.instance.project)
            self.initial['header'] = rendered['header']
            self.initial['footer'] = rendered['footer']

        self.calculate_totals([
            'estimate',
        ], lambda form: str(form['is_attached'].value()) == 'True')

    @atomic
    def save(self, commit=True):

        proposal = self.instance
        proposal.json = self.json

        doc_settings = DocumentSettings.get_for_language(get_language())
        proposal.letterhead = doc_settings.proposal_letterhead

        pdf_type.proposal.serialize(proposal)

        super().save(commit)

        proposal.jobs = self.formset.get_transaction_rows()


class BaseProposalFormSet(BaseDocumentFormSet):

    def clean(self):
        super().clean()
        if not self.get_transaction_rows():
            raise ValidationError(_("At least one job must be selected."))


class ProposalRowForm(DocumentRowForm):

    is_attached = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.estimate_amount = Amount.from_net(self.job.estimate_total, TAX_RATE)

    @property
    def json(self):
        if self.cleaned_data['is_attached']:
            return {
                'job': self.job,
                'job.id': self.job.id,
                'code': self.job.code,
                'name': self.job.name,
                'is_attached': True,
                'estimate': self.estimate_amount
            }

    @property
    def transaction(self):
        if self.cleaned_data['is_attached']:
            return self.job


ProposalFormSet = formset_factory(ProposalRowForm, formset=BaseProposalFormSet, extra=0)


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
