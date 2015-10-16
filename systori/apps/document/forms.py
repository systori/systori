from decimal import Decimal
from django import forms
from django.forms import widgets
from django.forms import Form
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _
from systori.lib.fields import LocalizedDecimalField
from .models import Proposal, Invoice, DocumentTemplate
from ..task.models import Job


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


class InvoiceDetailsForm(forms.ModelForm):
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
        fields = ['doc_template', 'is_final', 'document_date', 'invoice_no', 'title', 'header', 'footer', 'add_terms', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }


class InvoiceJobForm(Form):
    is_invoiced = forms.BooleanField(initial=True)
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.all(), widget=forms.HiddenInput())
    amount = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=4, required=False)


class BaseInvoiceForm(BaseFormSet):

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance')
        super().__init__(*args, prefix='job', initial=[{'job': job} for job in kwargs.pop('jobs', [])], **kwargs)
        self.details_form = InvoiceDetailsForm(*args, instance=instance, **kwargs)

    def is_valid(self):
        payment_valid = self.payment_form.is_valid()
        splits_valid = super().is_valid()
        return payment_valid and splits_valid

    def clean(self):
        splits = Decimal(0.0)
        for form in self.forms:
            if form.cleaned_data['amount']:
                splits += form.cleaned_data['amount']
        payment = self.payment_form.cleaned_data.get('amount', Decimal(0.0))
        if splits != payment:
            raise forms.ValidationError(_("The sum of splits must equal the prepayment amount."))

    def get_splits(self):
        splits = []
        for split in self.forms:
            if split.cleaned_data['amount']:
                job = split.cleaned_data['job']
                amount = split.cleaned_data['amount']
                splits.append((job, amount))
        return splits

InvoiceForm = formset_factory(InvoiceJobForm, formset=BaseInvoiceForm, extra=0)
