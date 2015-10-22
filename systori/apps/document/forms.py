from decimal import Decimal
from django import forms
from django.forms import widgets
from django.forms import Form
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _
from systori.lib.fields import LocalizedDecimalField
from .models import Proposal, Invoice, DocumentTemplate
from ..project.models import Project
from ..task.models import Job
from ..accounting import skr03
from ..accounting.constants import TAX_RATE
from .type import invoice


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


class InvoiceDocumentForm(forms.ModelForm):
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


class InvoiceDebitForm(Form):
    is_invoiced = forms.BooleanField(initial=True)
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.all(), widget=forms.HiddenInput())
    flat_amount = LocalizedDecimalField(label=_("Flat"), max_digits=14, decimal_places=4, required=False)
    debit_amount = forms.DecimalField(label=_("Debit"), initial=Decimal(0.0), max_digits=14, decimal_places=4, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = kwargs['initial']['job']
        self.estimate = self.job.estimate_total * (1+TAX_RATE)
        self.itemized = self.job.billable_total * (1+TAX_RATE)
        self.debited = self.job.account.debits().total
        self.balance = self.job.account.balance
        if self['is_invoiced'].value():
            possible_debit = self.itemized - self.debited
            if possible_debit > 0:
                self.initial['debit_amount'] = possible_debit
        self.debit_amount_decimal = Decimal(self['debit_amount'].value())
        self.debited_w_debit = self.debited + self.debit_amount_decimal
        self.balance_w_debit = self.balance + self.debit_amount_decimal


class BaseInvoiceForm(BaseFormSet):

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance')
        super().__init__(*args, prefix='job', initial=[{'job': job} for job in kwargs.pop('jobs', [])], **kwargs)
        self.document = InvoiceDocumentForm(*args, instance=instance, **kwargs)

        self.estimate_total = Decimal(0.0)
        self.itemized_total = Decimal(0.0)
        self.debit_total = Decimal(0.0)
        self.debited_total = Decimal(0.0)
        self.balance_total = Decimal(0.0)
        for form in self.forms:
            if form['is_invoiced'].value():
                self.estimate_total += form.estimate
                self.itemized_total += form.itemized
                self.debit_total += form.debit_amount_decimal
                self.debited_total += form.debited_w_debit
                self.balance_total += form.balance_w_debit

    def is_valid(self):
        document_valid = self.document.is_valid()
        debits_valid = super().is_valid()
        return document_valid and debits_valid

    def get_debits(self):
        debits = []
        for debit in self.forms:
            if debit.cleaned_data['is_invoiced']:
                job = debit.cleaned_data['job']
                amount = debit.cleaned_data['debit_amount']
                debits.append((job, amount))
        return debits

    def save(self):
        return

        #if details.cleaned_data['is_final']:
        #    for job in project.jobs.all():
        #        skr03.final_debit(job)
        #    project.begin_settlement()
        #    project.save()

        project = Project.prefetch(self.request.project.id)

        total = Decimal(0.0)
        debits = self.get_debits()
        for job, amount in debits:
            total += amount
            skr03.partial_debit(job, amount)

        json = invoice.serialize(project, debits, self.document.cleaned_data)

        self.document.instance.amount = total
        self.document.instance.json = json
        self.document.instance.json_version = json['version']
        self.document.save()


InvoiceForm = formset_factory(InvoiceDebitForm, formset=BaseInvoiceForm, extra=0)
