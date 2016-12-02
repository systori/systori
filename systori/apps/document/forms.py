from datetime import date
from decimal import Decimal as D
from types import SimpleNamespace

from django import forms
from django.forms.formsets import formset_factory
from django.conf import settings
from django.db import models, transaction
from django.utils.translation import get_language, ugettext_lazy as _

from systori.lib.fields import LocalizedDecimalField
from systori.lib.accounting.tools import Amount

from ..accounting.workflow import Account, credit_jobs, debit_jobs, adjust_jobs, refund_jobs
from ..accounting.constants import TAX_RATE
from ..accounting.models import Entry

from .models import Invoice, Adjustment, Payment, Refund, Proposal
from .models import DocumentTemplate, DocumentSettings, Letterhead
from .letterhead_utils import clean_letterhead_pdf

from . import type as pdf_type


def convert_field_to_value(field):
    try:
        value = field.value()
        amount = field.field.to_python(value)
        if amount is None:
            amount = D('0.00')
    except:
        amount = D('0.00')
    return amount


class DocumentForm(forms.ModelForm):

    class Meta:
        widgets = {
            'document_date': forms.widgets.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, formset_class, instance, jobs, **kwargs):
        super().__init__(*args, instance=instance, initial=kwargs.pop('initial', {}), **kwargs)
        self.formset = formset_class(instance=instance, jobs=jobs, **kwargs)

    def is_valid(self):
        form_valid = super().is_valid()
        formset_valid = self.formset.is_valid()
        return form_valid and formset_valid

    def calculate_totals(self, totals, condition=lambda form: True):

        for total in totals:
            total_field = total[:-4]+'total_diff_amount' if total.endswith('_diff') else total+'_total_amount'
            total_field = total_field.replace('.', '_')
            setattr(self, total_field, Amount.zero())

        for form in self.formset:
            if condition(form):
                for total in totals:
                    total_field = total[:-4]+'total_diff_amount' if total.endswith('_diff') else total+'_total_amount'
                    if '.' in total:
                        state_name, attr_name = total.split('.')
                        state = getattr(form, state_name)
                        form_amount = getattr(state, attr_name+'_amount')
                    else:
                        form_amount = getattr(form, total+'_amount')
                    total_field = total_field.replace('.', '_')
                    total_amount = getattr(self, total_field)
                    setattr(self, total_field, total_amount+form_amount)

    @property
    def json(self):
        json = {}

        # Contact Details
        contact = self.instance.project.billable_contact.contact
        json.update({
            'business': contact.business,
            'salutation': contact.salutation,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'address': contact.address,
            'postal_code': contact.postal_code,
            'city': contact.city,
            'address_label': contact.address_label
        })

        # Jobs
        json['jobs'] = self.formset.get_json_rows()

        # Totals
        for attr in dir(self):
            if attr.endswith('_total_amount'):
                json_name = attr[:-len('_amount')]
                if attr.startswith('pre_txn_'):
                    json_name = json_name[len('pre_txn_'):]
                json[json_name] = getattr(self, attr)

        # Document Type Specific Fields
        for field in self._meta.fields:
            value = self.cleaned_data[field]
            if isinstance(value, models.Model):
                json[field] = value.id
            else:
                json[field] = value

        return json


class BaseDocumentFormSet(forms.formsets.BaseFormSet):

    def __init__(self, *args, instance, jobs, **kwargs):
        super().__init__(*args, prefix='job', initial=self.get_initial(instance, jobs), **kwargs)
        self.instance = instance
        if hasattr(self.instance, 'transaction'):
            self.calculate_accounting_states()
            self.calculate_initial_values()

    def clean(self):
        for form in self:
            if form.job.id != form.cleaned_data['job_id']:
                raise forms.ValidationError(_("Form has become invalid due to external changes to the jobs list."))

    @staticmethod
    def get_initial(instance, jobs):
        initial = []
        for job in jobs:
            row = {
                'job': job,
                'jobs': jobs,
            }
            for json in instance.json['jobs']:
                if json['job.id'] == job.id:
                    row.update(json)
                    break
            initial.append(row)
        return initial

    def get_json_rows(self):
        return [form.json for form in self if form.json]

    def get_transaction_rows(self):
        return [form.transaction for form in self if form.transaction]

    def calculate_accounting_states(self):

        if self.instance.transaction:

            # Start Transaction
            atom = transaction.atomic()
            atom.__enter__()

            # Delete transaction entries so we can capture accounting state without it
            self.instance.transaction.entries.all().delete()

            # Capture state of accounting system before transaction
            for form in self:
                form.pre_txn = SimpleNamespace()
                form.calculate_accounting_state(form.pre_txn)

            # Rollback Transaction
            transaction.set_rollback(True)
            atom.__exit__(None, None, None)

        else:

            # Capture state of accounting system before transaction
            for form in self:
                form.pre_txn = SimpleNamespace()
                form.calculate_accounting_state(form.pre_txn)

    def calculate_initial_values(self):
        for form in self:
            form.calculate_initial_values()


class DocumentRowForm(forms.Form):
    job_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = self.initial['job']
        self.initial['job_id'] = self.job.id

    def init_amount(self, name):
        initial_amount = self.initial.get(name, Amount.zero())
        self.initial[name+'_net'] = initial_amount.net
        self.initial[name+'_tax'] = initial_amount.tax
        initial_or_updated_amount = Amount(
            convert_field_to_value(self[name+'_net']),
            convert_field_to_value(self[name+'_tax'])
        )
        setattr(self, name+'_amount', initial_or_updated_amount)

    def calculate_accounting_state(self, state):
        raise NotImplementedError()

    @property
    def json(self):
        raise NotImplementedError()

    @property
    def transaction(self):
        raise NotImplementedError()


class InvoiceForm(DocumentForm):

    doc_template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.filter(
            document_type=DocumentTemplate.INVOICE), required=False)

    add_terms = forms.BooleanField(label=_('Add Terms'), initial=True, required=False)
    is_final = forms.BooleanField(label=_('Is Final Invoice?'), initial=False, required=False)

    title = forms.CharField(label=_('Title'), initial=_("Invoice"))
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    class Meta(DocumentForm.Meta):
        model = Invoice
        fields = ['doc_template', 'document_date', 'invoice_no', 'is_final', 'title', 'header', 'footer', 'add_terms', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formset_class=InvoiceFormSet, **kwargs)

        if 'header' not in self.initial or 'footer' not in self.initial:
            default_text = DocumentSettings.get_for_language(settings.LANGUAGE_CODE)
            if default_text and default_text.invoice_text:
                rendered = default_text.invoice_text.render(self.instance.project)
                self.initial['header'] = rendered['header']
                self.initial['footer'] = rendered['footer']

        self.calculate_totals([
            'pre_txn.estimate',
            'pre_txn.progress',
            'pre_txn.invoiced',
            'pre_txn.balance',
            'pre_txn.itemized',
            'debit',
        ], lambda form: str(form['is_invoiced'].value()) == 'True')

        self.pre_txn_progress_total_percent = 0
        if self.pre_txn_estimate_total_amount.net > 0:
            self.pre_txn_progress_total_percent = self.pre_txn_progress_total_amount.net / self.pre_txn_estimate_total_amount.net * 100

        self.pre_txn_invoiced_total_percent = 0
        if self.pre_txn_progress_total_amount.net > 0:
            self.pre_txn_invoiced_total_percent = self.pre_txn_invoiced_total_amount.net / self.pre_txn_progress_total_amount.net * 100

    @transaction.atomic
    def save(self, commit=True):

        invoice = self.instance
        invoice.json = self.json

        if invoice.transaction:
            invoice.transaction.delete()

        invoice.transaction = debit_jobs(
            self.formset.get_transaction_rows(),
            recognize_revenue=self.cleaned_data['is_final']
        )

        doc_settings = DocumentSettings.get_for_language(get_language())
        invoice.letterhead = doc_settings.invoice_letterhead

        pdf_type.invoice.serialize(invoice)

        super().save(commit)


class BaseInvoiceFormSet(BaseDocumentFormSet):

    def clean(self):
        super().clean()
        if not self.get_transaction_rows():
            raise forms.ValidationError(_("At least one job must be selected."))


class InvoiceRowForm(DocumentRowForm):

    is_invoiced = forms.BooleanField(initial=False, required=False)

    debit_net = LocalizedDecimalField(label=_("Debit Net"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)
    debit_tax = LocalizedDecimalField(label=_("Debit Tax"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)

    is_override = forms.BooleanField(initial=False, required=False, widget=forms.HiddenInput())
    override_comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_accounting_state(self, state):

        state.estimate_amount = Amount.from_net(self.job.total, TAX_RATE)

        state.progress_amount = Amount.from_net(self.job.progress, TAX_RATE)
        state.progress_percent = self.job.progress_percent

        state.invoiced_amount = self.job.account.invoiced
        state.invoiced_percent = 0
        if state.progress_amount.net > 0:
            state.invoiced_percent = state.invoiced_amount.net / state.progress_amount.net * 100

        state.balance_amount = self.job.account.balance

        state.itemized_amount = state.progress_amount - state.invoiced_amount
        if state.itemized_amount.gross < 0:
            state.itemized_amount = Amount.zero()

    def calculate_initial_values(self):

        # on first load BooleanField.value() comes from self.initial and is an actual bool() type
        # on subsequent submits, value() returns a string from self.data, this makes
        # testing for truthyness difficult, so lets just always use the string version
        # unless you have self.cleaned_data available which is best
        self.is_invoiced_str = str(self['is_invoiced'].value())
        self.is_override_str = str(self['is_override'].value())

        if self.is_override_str == 'False':
            if self.pre_txn.itemized_amount.net > 0:
                self.initial['debit'] = self.pre_txn.itemized_amount

        if 'debit' not in self.initial:
            self.initial['debit'] = Amount.zero()
        self.init_amount('debit')

        self.post_txn = SimpleNamespace()
        self.post_txn.invoiced_amount = self.pre_txn.invoiced_amount + self.debit_amount
        self.post_txn.balance_amount = self.pre_txn.balance_amount + self.debit_amount

        self.is_itemized = True
        if self.post_txn.invoiced_amount != self.pre_txn.progress_amount:
            self.is_itemized = False

    def clean(self):
        if self.cleaned_data['is_override'] and \
                        self.debit_amount.gross > 0 and \
                        len(self.cleaned_data['override_comment'].strip()) == 0:
            self.add_error('override_comment', _("An explanation is required for non-itemized invoice."))

    @property
    def json(self):
        if self.cleaned_data['is_invoiced']:
            return {
                'job': self.job,
                'job.id': self.job.id,
                'code': self.job.code,
                'name': self.job.name,
                'is_invoiced': True,
                'debit': self.debit_amount,
                'is_itemized': self.is_itemized,
                'is_override': self.cleaned_data['is_override'],
                'override_comment': self.cleaned_data['override_comment'],
                'invoiced': self.post_txn.invoiced_amount,
                'balance': self.post_txn.balance_amount,
                'estimate': self.pre_txn.estimate_amount,
                'progress': self.pre_txn.progress_amount,
            }

    @property
    def transaction(self):
        if self.cleaned_data['is_invoiced']:
            debit_type = Entry.WORK_DEBIT
            if self.cleaned_data['is_override']:
                debit_type = Entry.FLAT_DEBIT
            if self.debit_amount.gross > 0:
                return self.job, self.debit_amount, debit_type


InvoiceFormSet = formset_factory(InvoiceRowForm, formset=BaseInvoiceFormSet, extra=0)


class AdjustmentForm(DocumentForm):

    title = forms.CharField(label=_('Title'), initial=_("Adjustment"), required=False)
    header = forms.CharField(widget=forms.Textarea, initial='', required=False)
    footer = forms.CharField(widget=forms.Textarea, initial='', required=False)

    class Meta:
        model = Adjustment
        fields = ['document_date', 'title', 'header', 'footer', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formset_class=AdjustmentFormSet, **kwargs)
        self.calculate_totals([
            'pre_txn.paid',
            'pre_txn.invoiced',
            'pre_txn.invoiced_diff',
            'pre_txn.progress',
            'pre_txn.progress_diff',
            'adjustment',
            'corrected',
        ])

    @transaction.atomic
    def save(self, commit=True):

        adjustment = self.instance
        adjustment.json = self.json

        if adjustment.transaction:
            adjustment.transaction.delete()

        adjustment.transaction = adjust_jobs(self.formset.get_transaction_rows())

        doc_settings = DocumentSettings.get_for_language(get_language())
        adjustment.letterhead = doc_settings.invoice_letterhead

        pdf_type.adjustment.serialize(adjustment)

        invoice = adjustment.invoice
        if invoice:
            invoice.set_adjustments(self.formset.get_json_rows())
            invoice.save()

        super().save(commit)


class AdjustmentRowForm(DocumentRowForm):

    adjustment_net = LocalizedDecimalField(label=_("Adjustment Net"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)
    adjustment_tax = LocalizedDecimalField(label=_("Adjustment Tax"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)

    corrected_net = LocalizedDecimalField(label=_("Corrected Net"), max_digits=14, decimal_places=2, required=False)
    corrected_tax = LocalizedDecimalField(label=_("Corrected Tax"), max_digits=14, decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_accounting_state(self, state):

        state.paid_amount = self.job.account.paid.negate

        state.invoiced_amount = self.job.account.invoiced
        state.invoiced_diff_amount = state.invoiced_amount - state.paid_amount

        state.progress_amount = Amount.from_net(self.job.progress, TAX_RATE)
        state.progress_diff_amount = state.progress_amount - state.invoiced_amount

    def calculate_initial_values(self):

        if 'invoiced' in self.initial:
            self.pre_txn.invoiced_amount = self.initial['invoiced']
            self.pre_txn.invoiced_diff_amount = Amount.zero()

        if 'corrected' not in self.initial:
            self.initial['corrected'] = self.pre_txn.invoiced_amount
        self.init_amount('corrected')

        if 'adjustment' not in self.initial:
            self.initial['adjustment'] = self.corrected_amount - self.pre_txn.invoiced_amount
        self.init_amount('adjustment')

    @property
    def json(self):
        return {
            'job.id': self.job.id,
            'code': self.job.code,
            'name': self.job.name,
            'progress': self.pre_txn.progress_amount,
            'paid': self.pre_txn.paid_amount,
            'invoiced': self.pre_txn.invoiced_amount,
            'adjustment': self.adjustment_amount,
            'corrected': self.corrected_amount
        }

    @property
    def transaction(self):
        return self.job, self.adjustment_amount


AdjustmentFormSet = formset_factory(AdjustmentRowForm, formset=BaseDocumentFormSet, extra=0)


class PaymentForm(DocumentForm):
    document_date = forms.DateField(label=_("Received Date"), initial=date.today, localize=True)
    bank_account = forms.ModelChoiceField(label=_("Bank Account"), queryset=Account.objects.banks())
    payment = LocalizedDecimalField(label=_("Payment"), max_digits=14, decimal_places=4)
    discount = forms.TypedChoiceField(
        label=_('Is discounted?'), coerce=D,
        choices=[
            ('0.00', _('0%')),
            ('0.01', _('1%')),
            ('0.02', _('2%')),
            ('0.03', _('3%')),
            ('0.04', _('4%')),
            ('0.05', _('5%')),
            ('0.06', _('6%')),
            ('0.07', _('7%')),
        ]
    )

    class Meta(DocumentForm.Meta):
        model = Payment
        fields = ['document_date', 'bank_account', 'payment', 'discount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formset_class=PaymentFormSet, **kwargs)
        self.payment_value = convert_field_to_value(self['payment'])
        self.calculate_totals([
            'balance',
            'split',
            'discount',
            'adjustment',
            'credit'
        ])

    def clean(self):
        splits = Amount.zero()
        for form in self.formset:
            splits += form.split_amount
        if splits.gross != self.payment_value:
            raise forms.ValidationError(_("The sum of splits must equal the payment amount."))

    @transaction.atomic
    def save(self, commit=True):

        payment = self.instance
        payment.json = self.json

        if payment.transaction:
            payment.transaction.delete()

        payment.transaction = credit_jobs(
            self.formset.get_transaction_rows(),
            self.cleaned_data['payment'],
            self.cleaned_data['document_date'],
            self.cleaned_data['bank_account']
        )

        doc_settings = DocumentSettings.get_for_language(get_language())
        payment.letterhead = doc_settings.invoice_letterhead

        pdf_type.payment.serialize(payment)

        invoice = payment.invoice

        if invoice:
            if not invoice.status == Invoice.PAID:
                invoice.pay()
            invoice.set_payment(self.formset.get_json_rows())
            invoice.save()

        super().save(commit)


class PaymentRowForm(DocumentRowForm):

    split_net = LocalizedDecimalField(label=_("Split Net"), max_digits=14, decimal_places=2, required=False)
    split_tax = LocalizedDecimalField(label=_("Split Tax"), max_digits=14, decimal_places=2, required=False)

    discount_net = LocalizedDecimalField(label=_("Discount Net"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())
    discount_tax = LocalizedDecimalField(label=_("Discount Tax"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())

    adjustment_net = LocalizedDecimalField(label=_("Adjustment Net"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())
    adjustment_tax = LocalizedDecimalField(label=_("Adjustment Tax"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_accounting_state(self, state):
        state.balance_amount = self.job.account.balance

    def calculate_initial_values(self):

        self.balance_amount = self.pre_txn.balance_amount
        if 'invoiced' in self.initial:
            # when paying an invoice, the balance is taken from invoice instead of accouting system
            self.balance_amount = self.initial['invoiced']

        self.init_amount('split')
        self.init_amount('discount')
        self.init_amount('adjustment')

        if self.balance_amount.gross < 0:
            self.balance_amount = Amount.zero()

        self.credit_amount = self.split_amount + self.discount_amount + self.adjustment_amount

    @property
    def json(self):
        if any((self.split_amount.gross, self.discount_amount.gross, self.adjustment_amount.gross)):
            json = {
                'job.id': self.job.id,
                'code': self.job.code,
                'name': self.job.name,
                'balance': self.balance_amount,
                'split': self.split_amount,
                'discount': self.discount_amount,
                'adjustment': self.adjustment_amount,
                'credit': self.credit_amount
            }
            if 'invoiced' in self.initial:
                json['invoiced'] = self.initial['invoiced']
            return json

    @property
    def transaction(self):
        if any((self.split_amount.gross, self.discount_amount.gross, self.adjustment_amount.gross)):
            return self.job, self.split_amount, self.discount_amount, self.adjustment_amount

PaymentFormSet = formset_factory(PaymentRowForm, formset=BaseDocumentFormSet, extra=0)


class RefundForm(DocumentForm):

    title = forms.CharField(label=_('Title'), initial=_("Refund"), required=False)
    header = forms.CharField(widget=forms.Textarea, initial='', required=False)
    footer = forms.CharField(widget=forms.Textarea, initial='', required=False)

    class Meta(DocumentForm.Meta):
        model = Refund
        fields = ['document_date', 'title', 'header', 'footer', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formset_class=RefundFormSet, **kwargs)

        if not self.instance.id:
            self.calculate_initial_refund()

        self.calculate_totals([
            'pre_txn.paid',
            'pre_txn.invoiced',
            'pre_txn.invoiced_diff',
            'pre_txn.progress',
            'pre_txn.progress_diff',
            'refund',
            'credit',
        ])

        self.customer_refund_amount = Amount.zero()
        if self.refund_total_amount.gross > self.credit_total_amount.gross:
            self.customer_refund_amount = self.refund_total_amount - self.credit_total_amount

    def calculate_initial_refund(self):
        refund_total = Amount.zero()
        for form in self.formset:
            refund_total += form.refund_amount
        for form in self.formset:
            refund_total = form.consume_refund(refund_total)
        return refund_total

    @transaction.atomic
    def save(self, commit=True):

        refund = self.instance
        refund.json = self.json
        refund.json.update({
            'customer_refund': self.customer_refund_amount
        })

        if refund.transaction:
            refund.transaction.delete()

        refund.transaction = refund_jobs(self.formset.get_transaction_rows())

        doc_settings = DocumentSettings.get_for_language(get_language())
        refund.letterhead = doc_settings.invoice_letterhead

        pdf_type.refund.serialize(refund)

        super().save(commit)


class RefundRowForm(DocumentRowForm):
    refund_net = LocalizedDecimalField(label=_("Refund Net"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)
    refund_tax = LocalizedDecimalField(label=_("Refund Tax"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)

    credit_net = LocalizedDecimalField(label=_("Apply Net"), max_digits=14, decimal_places=2, required=False)
    credit_tax = LocalizedDecimalField(label=_("Apply Tax"), max_digits=14, decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_accounting_state(self, state):
        # Paid Column
        state.paid_amount = self.job.account.paid.negate

        # Invoiced Column
        state.invoiced_amount = self.job.account.invoiced
        state.invoiced_diff_amount = state.invoiced_amount - state.paid_amount

        # Billable Column
        state.progress_amount = Amount.from_net(self.job.progress, TAX_RATE)
        state.progress_diff_amount = state.progress_amount - state.invoiced_amount

    def calculate_initial_values(self):

        # Refund Column
        if 'refund' not in self.initial and self.pre_txn.invoiced_amount.gross < self.pre_txn.paid_amount.gross:
            self.initial['refund'] = self.pre_txn.paid_amount - self.pre_txn.invoiced_amount
        self.init_amount('refund')

        # Apply Column
        self.init_amount('credit')

    def consume_refund(self, refund):
        if self.pre_txn.progress_amount.gross > self.pre_txn.paid_amount.gross:
            consumable = self.pre_txn.progress_amount - self.pre_txn.paid_amount
            if refund.gross < consumable.gross:
                consumable = refund
            self.initial['credit'] = consumable
            self.init_amount('credit')
            refund -= consumable
        return refund

    @property
    def json(self):
        return {
            'job.id': self.job.id,
            'code': self.job.code,
            'name': self.job.name,
            'paid': self.pre_txn.paid_amount,
            'invoiced': self.pre_txn.invoiced_amount,
            'progress': self.pre_txn.progress_amount,
            'refund': self.refund_amount,
            'credit': self.credit_amount
        }

    @property
    def transaction(self):
        return self.job, self.refund_amount, self.credit_amount

RefundFormSet = formset_factory(RefundRowForm, formset=BaseDocumentFormSet, extra=0)



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

    @transaction.atomic
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
            raise forms.ValidationError(_("At least one job must be selected."))


class ProposalRowForm(DocumentRowForm):

    is_attached = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.estimate_amount = Amount.from_net(self.job.total, TAX_RATE)

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

    class Meta:
        model = Letterhead
        fields = ['letterhead_pdf']

    def clean(self):
        clean_letterhead_pdf(self.cleaned_data.get('letterhead_pdf'))

    def save(self):
        return clean_letterhead_pdf(self.cleaned_data.get('letterhead_pdf'), save=True)


class LetterheadUpdateForm(forms.ModelForm):

    class Meta:
        model = Letterhead
        exclude = []


class DocumentSettingsForm(forms.ModelForm):

    class Meta:
        model = DocumentSettings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proposal_text'].queryset = DocumentTemplate.objects.filter(document_type=DocumentTemplate.PROPOSAL)
        self.fields['invoice_text'].queryset = DocumentTemplate.objects.filter(document_type=DocumentTemplate.INVOICE)
