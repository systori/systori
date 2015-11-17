from decimal import Decimal
from django import forms
from django.conf import settings
from django.forms import widgets
from django.forms import Form, ValidationError
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _
from systori.lib.fields import LocalizedDecimalField
from .models import Proposal, Invoice, DocumentTemplate, Letterhead, DocumentSettings
from ..project.models import Project
from ..task.models import Job
from ..accounting import skr03
from ..accounting.constants import TAX_RATE
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_text = DocumentSettings.get_for_language(settings.LANGUAGE_CODE)
        if default_text and default_text.invoice_text:
            rendered = default_text.invoice_text.render(self.instance.project)
            self.initial['header'] = rendered['header']
            self.initial['footer'] = rendered['footer']

    class Meta:
        model = Invoice
        fields = ['parent', 'doc_template', 'is_final', 'document_date', 'invoice_no', 'title', 'header', 'footer', 'add_terms', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Invoice.objects.filter(project=self.instance.project)


class InvoiceDebitForm(Form):

    is_invoiced = forms.BooleanField(initial=True, required=False)
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.none(), widget=forms.HiddenInput())
    flat_amount = LocalizedDecimalField(label=_("Flat"), max_digits=14, decimal_places=2, required=False)
    is_flat = forms.BooleanField(initial=False, required=False, widget=forms.HiddenInput())
    debit_amount = forms.DecimalField(label=_("Debit"), initial=Decimal(0.0), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())
    debit_comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = self.initial['job']
        self.setup_accounting_data()
        self.fields['job'].queryset = self.job.project.jobs.all()
        self.fields['flat_amount'].widget.attrs['class'] = 'form-control'
        if str(self['is_invoiced'].value()) == 'False':
            self.fields['flat_amount'].widget.attrs['disabled'] = True
        self.fields['debit_comment'].widget.attrs['class'] = 'job-debit-comment form-control'
        del self.fields['debit_comment'].widget.attrs['cols']
        del self.fields['debit_comment'].widget.attrs['rows']

    def clean(self):
        if self.cleaned_data['is_flat'] and\
                len(self.cleaned_data['debit_comment']) < 2:
            self.add_error('debit_comment',
                    ValidationError(_("A comment is required for flat invoice.")))

    def get_dict(self):
        """
        This dictionary later becomes the 'initial' value to this form when
        editing the invoice.
        """
        return {
            'job': self.job,
            'is_invoiced': self.cleaned_data['is_invoiced'],
            'flat_amount': self.cleaned_data['flat_amount'],
            'is_flat': self.cleaned_data['is_flat'],
            'debit_amount': self.cleaned_data['debit_amount'],
            'debit_comment': self.cleaned_data['debit_comment'],
            'debited': self.latest_debited,
            'balance': self.latest_balance,
            'estimate': self.latest_estimate,
            'itemized': self.latest_itemized,
        }

    def setup_accounting_data(self):
        self.latest_estimate = round(self.job.estimate_total * (1+TAX_RATE), 2)
        self.latest_itemized = round(self.job.billable_total * (1+TAX_RATE), 2)

        if self.initial['is_booked']:
            # debit_amount comes in as a float from JSONField and as a string from form submission
            # but we need it as a Decimal for pretty much everything
            self.debit_amount_decimal = Decimal(str(self['debit_amount'].value()))

            # this debit is already in accounting system, so we subtract it to get pre-debit totals
            self.original_debit_amount = Decimal(str(self.initial['debit_amount']))
            self.latest_debited = self.job.account.debits().total
            self.latest_balance = self.job.account.balance
            self.latest_debited_base = self.latest_debited - self.original_debit_amount
            self.latest_balance_base = self.latest_balance - self.original_debit_amount

            # update debit_amount for itemized invoices in case 'work completed' has changed
            if str(self.initial['is_flat']) == 'False':
                updated_debit = self.latest_itemized - self.latest_debited_base
                self.debit_amount_decimal = updated_debit if updated_debit > 0 else Decimal(0.0)
                self.initial['debit_amount'] = self.debit_amount_decimal

            # previous values come from json, could be different from latest values
            self.previous_debited = Decimal(self.initial['debited'])
            self.previous_balance = Decimal(self.initial['balance'])
            self.previous_estimate = Decimal(self.initial['estimate'])
            self.previous_itemized = Decimal(self.initial['itemized'])

        else:
            # no transactions exist yet so the totals don't include debit, we add to final totals
            self.latest_debited_base = self.job.account.debits().total
            self.latest_balance_base = self.job.account.balance
            if str(self['is_invoiced'].value()) == 'True' and str(self['is_flat'].value()) == 'False':
                possible_debit = self.latest_itemized - self.latest_debited_base
                self.initial['debit_amount'] = possible_debit if possible_debit > 0 else Decimal(0.0)
            self.original_debit_amount = self.debit_amount_decimal = Decimal(str(self['debit_amount'].value()))
            self.latest_debited = self.latest_debited_base + self.debit_amount_decimal
            self.latest_balance = self.latest_balance_base + self.debit_amount_decimal

            # latest and previous are the same
            self.previous_debited = self.latest_debited
            self.previous_balance = self.latest_balance
            self.previous_estimate = self.latest_estimate
            self.previous_itemized = self.latest_itemized

        # used to show user what has changed since last time invoice was created/edited
        self.diff_debited = self.latest_debited - self.previous_debited
        self.diff_balance = self.latest_balance - self.previous_balance
        self.diff_estimate = self.latest_estimate - self.previous_estimate
        self.diff_itemized = self.latest_itemized - self.previous_itemized
        self.diff_debit_amount = self.debit_amount_decimal - self.original_debit_amount


class BaseInvoiceForm(BaseFormSet):

    def __init__(self, *args, instance, jobs, **kwargs):
        super().__init__(*args, prefix='job', initial=self.get_initial(instance, jobs), **kwargs)
        self.invoice_form = InvoiceDocumentForm(*args, instance=instance, initial=instance.json, **kwargs)

        self.estimate_total = Decimal(0.0)
        self.itemized_total = Decimal(0.0)
        self.debit_total = Decimal(0.0)
        self.debited_total = Decimal(0.0)
        self.balance_total = Decimal(0.0)
        for form in self.forms:
            if form['is_invoiced'].value():
                self.estimate_total += form.latest_estimate
                self.itemized_total += form.latest_itemized
                self.debit_total += form.debit_amount_decimal
                self.debited_total += form.latest_debited
                self.balance_total += form.latest_balance

    def get_initial(self, invoice, jobs):
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

    def save(self):

        invoice = self.invoice_form.instance

        if invoice.transaction:
            invoice.transaction.delete()

        debits = []
        for debit_form in self.forms:
            if debit_form.cleaned_data['is_invoiced']:
                debits.append(debit_form.get_dict())

        data = self.invoice_form.cleaned_data

        skr03_debits = [(debit['job'], debit['debit_amount'], debit['is_flat']) for debit in debits]
        if data['is_final']:
            invoice.transaction = skr03.final_debit(skr03_debits)
        else:
            invoice.transaction = skr03.partial_debit(skr03_debits)
        invoice.save()

        del data['doc_template']  # don't need this

        data['debits'] = debits

        data['debit_gross'] = self.debit_total
        data['debit_net'] = round(self.debit_total / (1+TAX_RATE), 2)
        data['debit_tax'] = data['debit_gross'] - data['debit_net']

        data['debited_gross'] = self.debited_total
        data['debited_net'] = round(self.debited_total / (1+TAX_RATE), 2)
        data['debited_tax'] = data['debited_gross'] - data['debited_net']

        data['balance_gross'] = self.balance_total
        data['balance_net'] = round(self.balance_total / (1+TAX_RATE), 2)
        data['balance_tax'] = data['balance_gross'] - data['balance_net']

        json = invoice_lib.serialize(invoice, data)

        invoice.amount = data['debit_gross']
        invoice.json = json
        invoice.json_version = json['version']
        invoice.save()

InvoiceForm = formset_factory(InvoiceDebitForm, formset=BaseInvoiceForm, extra=0)


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
