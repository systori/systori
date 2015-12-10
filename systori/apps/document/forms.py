from decimal import Decimal
from django import forms
from django.conf import settings
from django.forms import widgets
from django.forms import Form, ValidationError
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _
from django.db.transaction import atomic
from systori.lib.fields import LocalizedDecimalField
from .models import Proposal, Invoice, DocumentTemplate, Letterhead, DocumentSettings
from ..project.models import Project
from ..task.models import Job
from ..accounting import workflow
from ..accounting.constants import TAX_RATE
from ..accounting.forms import BaseDebitTransactionForm, DebitForm
from .type import invoice as invoice_lib
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


class InvoiceDocumentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Invoice.objects.none(), required=False, widget=forms.HiddenInput())
    doc_template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.filter(
            document_type=DocumentTemplate.INVOICE), required=False)
    add_terms = forms.BooleanField(label=_('Add Terms'), initial=True, required=False)
    is_final = forms.BooleanField(label=_('Is Final Invoice?'), initial=False, required=False)

    title = forms.CharField(label=_('Title'), initial=_("Invoice"))
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Invoice
        fields = ['parent', 'doc_template', 'is_final', 'document_date', 'invoice_no', 'title', 'header', 'footer', 'add_terms', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Invoice.objects.filter(project=self.instance.project)
        if not self.initial.get('header', None) or not self.initial.get('footer', None):
            default_text = DocumentSettings.get_for_language(settings.LANGUAGE_CODE)
            if default_text and default_text.invoice_text:
                rendered = default_text.invoice_text.render(self.instance.project)
                self.initial['header'] = rendered['header']
                self.initial['footer'] = rendered['footer']


class BaseInvoiceForm(BaseDebitTransactionForm):

    def __init__(self, *args, instance, jobs, **kwargs):
        super().__init__(*args, initial=self.get_initial(instance, jobs), **kwargs)
        self.invoice_form = InvoiceDocumentForm(*args, instance=instance, initial=instance.json, **kwargs)

    @staticmethod
    def get_initial(invoice, jobs):
        initial = []
        previous_debits = invoice.json['debits']
        for job in jobs:

            job_dict = {
                'is_invoiced': False if previous_debits else True,
                'is_booked': False
            }

            for debit in previous_debits:
                if debit['job.id'] == job.id:
                    job_dict = debit.copy()
                    job_dict['is_booked'] = debit.get('is_booked', True)
                    break

            job_dict['job'] = job

            initial.append(job_dict)
        return initial

    def is_valid(self):
        invoice_valid = self.invoice_form.is_valid()
        debits_valid = super().is_valid()
        return invoice_valid and debits_valid

    @atomic
    def save(self):

        invoice = self.invoice_form.instance


        data = self.invoice_form.cleaned_data
        del data['doc_template']  # don't need this

        invoice.letterhead = Letterhead.objects.first()

        old_transaction = invoice.transaction

        invoice.transaction = self.save_debits(data['is_final'])
        invoice.save()

        if old_transaction:
            old_transaction.delete()

        data.update(self.get_data())

        json = invoice_lib.serialize(invoice, data)

        invoice.amount = data['debit_gross']
        invoice.json = json
        invoice.json_version = json['version']
        invoice.save()


InvoiceForm = formset_factory(DebitForm, formset=BaseInvoiceForm, extra=0)


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
