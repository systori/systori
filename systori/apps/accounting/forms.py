from datetime import date
from decimal import Decimal as D
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.forms import Form, ModelForm, ValidationError, widgets
from django.db.transaction import atomic
from django import forms
from systori.lib.fields import LocalizedDecimalField
from systori.lib.accounting.tools import Amount, round as _round
from ..task.models import Job
from .workflow import Account, credit_jobs, debit_jobs, adjust_jobs
from .constants import TAX_RATE, BANK_CODE_RANGE
from .models import Entry
from ..document.models import Invoice, Adjustment, Refund, DocumentTemplate, DocumentSettings
from ..document.type import invoice as invoice_lib
from ..document.type import refund as refund_lib
from ..document.type import adjustment as adjustment_lib
from .report import create_payments_report, create_adjustment_report, create_refund_report


def convert_field_to_value(field):
    try:
        value = field.value()
        amount = field.field.to_python(value)
        if amount is None:
            amount = D('0.00')
    except:
        amount = D('0.00')
    return amount


class InvoiceForm(forms.ModelForm):
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


class BaseInvoiceFormSet(BaseFormSet):

    def __init__(self, *args, instance, jobs, **kwargs):
        super().__init__(*args, prefix='job', initial=self.get_initial(instance, jobs), **kwargs)
        self.invoice_form = InvoiceForm(*args, instance=instance, initial=instance.json, **kwargs)
        self.estimate_total = Amount.zero()
        self.itemized_total = Amount.zero()
        self.debit_total = Amount.zero()
        self.debited_total = Amount.zero()
        self.balance_total = Amount.zero()
        for form in self.forms:
            if form['is_invoiced'].value():
                self.estimate_total += form.latest_estimate
                self.itemized_total += form.latest_itemized
                self.debit_total += form.debit_amount
                self.debited_total += form.new_debited
                self.balance_total += form.new_balance

    def is_valid(self):
        invoice_valid = self.invoice_form.is_valid()
        debits_valid = super().is_valid()
        return invoice_valid and debits_valid

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

    def get_data(self):

        return {
            'debits': self.debits,

            'debit_gross': self.debit_total.gross,
            'debit_net': self.debit_total.net,
            'debit_tax': self.debit_total.tax,

            'debited_gross': self.debited_total.gross,
            'debited_net': self.debited_total.net,
            'debited_tax': self.debited_total.tax,

            'balance_gross': self.balance_total.gross,
            'balance_net': self.balance_total.net,
            'balance_tax': self.balance_total.tax
        }

    @atomic
    def save(self):

        self.debits = []
        for debit_form in self.forms:
            if debit_form.cleaned_data['is_invoiced']:
                self.debits.append(debit_form.get_initial())
        jobs = [d['job'] for d in self.debits]

        invoice = self.invoice_form.instance
        data = self.invoice_form.cleaned_data
        data.update(self.get_data())

        if invoice.transaction:
            invoice.transaction.delete()

        skr03_debits = [(debit['job'], Amount.from_gross(debit['amount_gross'], TAX_RATE), Entry.FLAT_DEBIT if debit['is_override'] else Entry.WORK_DEBIT) for debit in self.debits]
        invoice.transaction = debit_jobs(skr03_debits, recognize_revenue=data['is_final'])

        doc_settings = DocumentSettings.get_for_language(get_language())

        invoice.letterhead = doc_settings.invoice_letterhead
        invoice.json = invoice_lib.serialize(invoice, data)
        invoice.save()

        # prepare_transaction_report expects the new transaction and invoice to already be in the database

        invoice.json.update(create_payments_report(jobs))
        invoice.save()


class InvoiceRowForm(Form):
    """ Represents a debit line for a single job/receivables account on an invoice. """

    is_invoiced = forms.BooleanField(initial=True, required=False)
    job = forms.ModelChoiceField(queryset=Job.objects.none(), widget=forms.HiddenInput())
    amount_net = LocalizedDecimalField(initial=D('0.00'), max_digits=14, decimal_places=2, required=False)
    is_override = forms.BooleanField(initial=False, required=False, widget=forms.HiddenInput())
    override_comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = self.initial['job']

        self.fields['job'].queryset = self.job.project.jobs.all()
        self.fields['amount_net'].widget.attrs['class'] = 'form-control'
        if str(self['is_invoiced'].value()) == 'False':
            self.fields['amount_net'].widget.attrs['disabled'] = True
        comment_attrs = self.fields['override_comment'].widget.attrs
        comment_attrs['class'] = 'job-override-comment form-control'
        del comment_attrs['cols']
        del comment_attrs['rows']

        self.latest_estimate = Amount.from_net(self.job.estimate_total, TAX_RATE)
        self.latest_itemized = Amount.from_net(self.job.billable_total, TAX_RATE)
        self.latest_percent_complete = self.job.complete_percent

        _initial_debit_amount_net = _round(D(self.initial.get('amount_net', self['amount_net'].field.initial)))
        initial_debit_amount = Amount.from_net(_initial_debit_amount_net, TAX_RATE)
        self.debit_amount = Amount.from_net(convert_field_to_value(self['amount_net']), TAX_RATE)

        if self.initial['is_booked']:
            # accounting system already has the 'new' amounts since this invoice was booked
            self.new_debited = self.job.account.invoiced
            self.new_balance = self.job.account.balance

            # we need to undo the booking to get the 'base' amounts
            self.base_debited = self.new_debited - initial_debit_amount
            self.base_balance = self.new_balance - initial_debit_amount

        else:
            # no transactions exist yet so the account balance and debits don't include this new debit
            # accounting system has the 'base' amounts
            self.base_debited = self.job.account.invoiced
            self.base_balance = self.job.account.balance

        # subtract all previous debits from all work completed to get amount not yet debited
        self.billable_amount = self.latest_itemized - self.base_debited

        if str(self['is_override'].value()) == 'False':
            if self.billable_amount.net > 0:
                self.debit_amount = self.billable_amount
            else:
                self.debit_amount = Amount.zero()
            # we want this updated on first load (self.initial) and subsequent reloads (self.data)
            self.initial['amount_net'] = self.debit_amount.net
            if self.data:
                self.data['amount_net'] = self.initial['amount_net']

        # now that we know the correct debit amount we can calculate what the new balance will be
        self.new_debited = self.base_debited + self.debit_amount
        self.new_balance = self.base_balance + self.debit_amount

        self.new_debited_percent = 0
        if self.latest_estimate.net > 0:
            if self.new_debited.net >= self.latest_estimate.net:
                self.new_debited_percent = 100
            else:
                self.new_debited_percent = round((self.new_debited.net / self.latest_estimate.net) * 100, 2)

        if self.initial['is_booked']:
            # previous values come from json, could be different from latest values
            self.previous_debited = Amount.from_gross(D(str(self.initial['debited_gross'])), TAX_RATE)
            self.previous_balance = Amount.from_gross(D(str(self.initial['balance_gross'])), TAX_RATE)
            self.previous_estimate = Amount.from_net(D(str(self.initial['estimate_net'])), TAX_RATE)
            self.previous_itemized = Amount.from_net(D(str(self.initial['itemized_net'])), TAX_RATE)
        else:
            # latest and previous are the same when there is nothing booked yet
            self.previous_debited = self.new_debited
            self.previous_balance = self.new_balance
            self.previous_estimate = self.latest_estimate
            self.previous_itemized = self.latest_itemized

        # used to show user what has changed since last time invoice was created/edited
        self.diff_debited = self.new_debited - self.previous_debited
        self.diff_balance = self.new_balance - self.previous_balance
        self.diff_estimate = self.latest_estimate - self.previous_estimate
        self.diff_itemized = self.latest_itemized - self.previous_itemized
        self.diff_debit_amount = self.debit_amount - initial_debit_amount

    def clean(self):
        if self.cleaned_data['is_override'] and \
                        len(self.cleaned_data['override_comment']) < 2:
            self.add_error('override_comment',
                           ValidationError(_("A comment is required for flat invoice.")))

    def get_initial(self):
        """
        This dictionary later becomes the 'initial' value to this form when
        editing the invoice.
        """
        return {
            'job': self.job,
            'is_invoiced': self.cleaned_data['is_invoiced'],
            'amount_net': self.debit_amount.net,
            'amount_gross': self.debit_amount.gross,
            'amount_tax': self.debit_amount.tax,
            'is_override': self.cleaned_data['is_override'],
            'override_comment': self.cleaned_data['override_comment'],
            'debited_gross': self.new_debited.gross,
            'debited_net': self.new_debited.net,
            'debited_tax': self.new_debited.tax,
            'balance_gross': self.new_balance.gross,
            'balance_net': self.new_balance.net,
            'balance_tax': self.new_balance.tax,
            'estimate_net': self.latest_estimate.net,
            'itemized_net': self.latest_itemized.net,
        }


InvoiceFormSet = formset_factory(InvoiceRowForm, formset=BaseInvoiceFormSet, extra=0)


class AdjustmentForm(forms.ModelForm):
    invoice = forms.ModelChoiceField(label=_("Invoice"), queryset=Invoice.objects.all(), widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Adjustment
        fields = ['invoice']

    def __init__(self, *args, jobs, instance, initial={}, **kwargs):
        super().__init__(*args, instance=instance, initial=initial, **kwargs)
        self.formset = AdjustmentFormSet(*args, jobs=jobs, adjustment=instance, **kwargs)

    def is_valid(self):
        adjustment_valid = super().is_valid()
        formset_valid = self.formset.is_valid()
        return adjustment_valid and formset_valid

    @atomic
    def save(self):

        adjustment = self.instance

        if adjustment.transaction:
            adjustment.transaction.delete()

        adjustment.transaction = adjust_jobs(self.formset.get_credit_tuples())

        doc_settings = DocumentSettings.get_for_language(get_language())

        adjustment.letterhead = doc_settings.invoice_letterhead
        adjustment.json = adjustment_lib.serialize(adjustment, {})
        adjustment.save()


class BaseAdjustmentFormSet(BaseFormSet):

    def __init__(self, *args, jobs, adjustment, **kwargs):
        super().__init__(*args, prefix='job', initial=self.get_initial(jobs, adjustment), **kwargs)
        self.paid_total = Amount.zero()
        self.invoiced_total = Amount.zero()
        self.invoiced_total_diff = Amount.zero()
        self.billable_total = Amount.zero()
        self.billable_total_diff = Amount.zero()
        self.approved_total = Amount.zero()
        self.adjustment_total = Amount.zero()
        for form in self.forms:
            self.paid_total += form.paid_amount
            self.invoiced_total += form.invoiced_amount
            self.invoiced_total_diff += form.invoiced_amount_diff
            self.billable_total += form.billable_amount
            self.billable_total_diff += form.billable_amount_diff
            self.approved_total += form.approved_amount
            self.adjustment_total += form.adjustment_amount

    def get_initial(self, jobs, adjustment):
        initial = []
        previous_credits = adjustment.json['credits']
        for job in jobs:
            job_dict = {}
            for credit in previous_credits:
                if credit['job.id'] == job.id:
                    job_dict['adjusted'] = credit['amount']
                    break
            job_dict['job'] = job
            initial.append(job_dict)
        return initial

    def get_credit_tuples(self):
        amounts = []
        for form in self.forms:
            job = form.cleaned_data['job']
            amounts.append((job, form.adjustment_amount, Amount.zero(), Amount.zero()))
        return amounts


class AdjustmentRowForm(Form):

    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.all(), widget=forms.HiddenInput())

    approved_net = LocalizedDecimalField(label=_("Approved Net"), max_digits=14, decimal_places=2, required=False)
    approved_tax = LocalizedDecimalField(label=_("Approved Tax"), max_digits=14, decimal_places=2, required=False)

    adjustment_net = LocalizedDecimalField(label=_("Adjustment Net"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)
    adjustment_tax = LocalizedDecimalField(label=_("Adjustment Tax"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = self.initial['job']

        self.fields['job'].queryset = Job.objects.filter(id=self.job.id)

        # Paid Column
        self.paid_amount = self.job.account.paid.negate

        # Invoiced Column
        if 'invoiced' in self.initial:
            self.invoiced_amount = self.initial['invoiced']
        else:
            self.invoiced_amount = self.job.account.invoiced
        self.invoiced_amount_diff = self.invoiced_amount - self.paid_amount

        # Billable Column
        self.billable_amount = Amount.from_net(self.job.billable_total, TAX_RATE)
        self.billable_amount_diff = self.billable_amount - self.invoiced_amount

        self.initial['approved_net'] = self.invoiced_amount.net
        self.initial['approved_tax'] = self.invoiced_amount.tax

        self.approved_amount = Amount(
            convert_field_to_value(self['approved_net']),
            convert_field_to_value(self['approved_tax'])
        )

        self.adjustment_amount = Amount(
            convert_field_to_value(self['adjustment_net']),
            convert_field_to_value(self['adjustment_tax'])
        )

    def clean(self):
        if self.adjustment_amount.gross > self.invoiced_amount.gross:
            self.add_error('adjustment_net', ValidationError(_("Adjustment cannot be greater than invoiced amount.")))


AdjustmentFormSet = formset_factory(AdjustmentRowForm, formset=BaseAdjustmentFormSet, extra=0)


class PaymentForm(Form):
    bank_account = forms.ModelChoiceField(label=_("Bank Account"), queryset=Account.objects.banks())
    amount = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=4)
    transacted_on = forms.DateField(label=_("Received Date"), initial=date.today, localize=True)
    invoice = forms.ModelChoiceField(label=_("Invoice"), queryset=Invoice.objects.all(), widget=forms.HiddenInput(), required=False)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount_value = Amount.from_gross(convert_field_to_value(self['amount']), TAX_RATE)


class BasePaymentFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        self.invoice = initial.get('invoice')
        super().__init__(*args, prefix='split', initial=self.get_initial(kwargs.pop('jobs', [])), **kwargs)
        self.payment_form = PaymentForm(*args, initial=initial, **kwargs)
        self.balance_total = Amount.zero()
        self.payment_total = Amount.zero()
        self.discount_total = Amount.zero()
        self.credit_total = Amount.zero()
        for form in self.forms:
            self.balance_total += form.balance_amount
            self.payment_total += form.payment_amount
            self.discount_total += form.discount_amount
            self.credit_total += form.credit_amount

    def get_initial(self, jobs):
        initial = []
        previous_debits = self.invoice.json['debits'] if self.invoice else []
        for job in jobs:
            job_dict = {}
            for debit in previous_debits:
                if debit['job.id'] == job.id:
                    job_dict['invoiced'] = job_dict['payment'] = debit['amount']
                    break
            job_dict['job'] = job
            initial.append(job_dict)
        return initial

    def is_valid(self):
        payment_valid = self.payment_form.is_valid()
        splits_valid = super().is_valid()
        return payment_valid and splits_valid

    def clean(self):
        splits = Amount.zero()
        for form in self.forms:
            splits += form.payment_amount
        payment = self.payment_form.cleaned_data.get('amount', D(0.0))
        if splits.gross != payment:
            raise forms.ValidationError(_("The sum of splits must equal the payment amount."))

    def get_splits(self):
        splits = []
        for split in self.forms:
            if split.payment_amount.gross > 0:
                job = split.cleaned_data['job']
                splits.append((job, split.payment_amount,  split.discount_amount, Amount.zero()))
        return splits

    def save(self):
        credit_jobs(
            self.get_splits(),
            self.payment_form.cleaned_data['amount'],
            self.payment_form.cleaned_data['transacted_on'],
            self.payment_form.cleaned_data['bank_account']
        )
        if self.invoice and not self.invoice.status == Invoice.PAID:
            self.invoice.pay()
            self.invoice.save()


class PaymentRowForm(Form):
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.all(), widget=forms.HiddenInput())

    payment_net = LocalizedDecimalField(label=_("Amount Net"), max_digits=14, decimal_places=2, required=False)
    payment_tax = LocalizedDecimalField(label=_("Amount Tax"), max_digits=14, decimal_places=2, required=False)

    discount_net = LocalizedDecimalField(label=_("Discount Net"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())
    discount_tax = LocalizedDecimalField(label=_("Discount Tax"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = self.initial['job']

        self.fields['job'].queryset = Job.objects.filter(id=self.job.id)

        for column_name in ['payment', 'discount']:
            net = convert_field_to_value(self[column_name+'_net'])
            tax = convert_field_to_value(self[column_name+'_tax'])
            setattr(self, column_name+'_amount', Amount(net, tax))

        if 'invoiced' in self.initial:
            self.balance_amount = self.initial['invoiced']
        else:
            self.balance_amount = self.job.account.balance

        self.credit_amount = self.payment_amount + self.discount_amount


PaymentFormSet = formset_factory(PaymentRowForm, formset=BasePaymentFormSet, extra=0)


class RefundForm(forms.ModelForm):
    title = forms.CharField(label=_('Title'), initial=_("Refund"))
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Refund
        fields = ['document_date', 'title', 'header', 'footer']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, instance, jobs, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        self.refund_jobs_form = RefundFormSet(prefix='refund', initial=self.get_initial(jobs), **kwargs)
        if len(jobs) <= 1:
            not_overpaid_jobs = []  # if there is only one job, no sense to allow applying to the same job
        else:
            not_overpaid_jobs = [form.initial['job'] for form in self.refund_jobs_form.forms if form.overpaid_value <= 0]
        self.apply_jobs_form = RefundFormSet(refund_total=self.refund_jobs_form.amount_total,
                                                prefix='apply', initial=self.get_initial(not_overpaid_jobs),
                                                **kwargs)
        self.refund_amount = self.refund_jobs_form.amount_total - self.apply_jobs_form.amount_total

    @staticmethod
    def get_initial(jobs):
        initial = []
        for job in jobs:
            job_dict = {
                'job': job,
            }
            initial.append(job_dict)
        return initial

    def is_valid(self):
        return self.refund_jobs_form.is_valid() and \
               self.apply_jobs_form.is_valid() and \
               super().is_valid()

    @atomic
    def save(self):

        refund = self.instance

        refunded = self.refund_jobs_form.get_amounts()
        applied = self.apply_jobs_form.get_amounts()
        refund_total = self.refund_jobs_form.amount_total - self.apply_jobs_form.amount_total

        data = self.cleaned_data.copy()
        data.update({
            'amount': refund_total
        })

        refund.transaction = refund_jobs(refunded, applied)

        doc_settings = DocumentSettings.get_for_language(get_language())

        refund.letterhead = doc_settings.invoice_letterhead
        refund.json = refund_lib.serialize(refund, data)
        refund.save()


class BaseRefundFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.applicable_refund_total = kwargs.pop('refund_total', D('0.00'))
        super().__init__(*args, **kwargs)
        self.amount_total = D('0.00')
        self.invoiced_total = D('0.00')
        self.payments_total = D('0.00')
        self.overpaid_total = D('0.00')
        self.underpaid_total = D('0.00')
        for form in self.forms:
            self.amount_total += form.amount_value
            self.invoiced_total += form.invoiced_value
            self.payments_total += form.payments_value
            self.overpaid_total += form.overpaid_value
            self.underpaid_total += form.underpaid_value

    def calculate_refund(self):
        refund_total = Amount.zero()
        for form in self.forms:
            refund_total += form.refund_amount
        for form in self.forms:
            refund_total = form.consume_refund(refund_total)

    def get_amounts(self):
        amounts = []
        for form in self.forms:
            if form.cleaned_data['amount']:
                job = form.cleaned_data['job']
                amount = form.cleaned_data['amount']
                amounts.append((job, amount))
        return amounts

    def clean(self):
        if self.prefix == 'apply':
            applied = D(0.0)
            for form in self.forms:
                if form.cleaned_data['amount']:
                    applied += form.cleaned_data['amount']
            if applied > self.applicable_refund_total:
                raise forms.ValidationError(_("Amount applied must be less than or equal to the refund amount."))


class RefundRowForm(Form):
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.all(), widget=forms.HiddenInput())
    amount = LocalizedDecimalField(label=_("Amount"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)

    refund_net = forms.DecimalField(label=_("Refund Net"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())
    refund_tax = forms.DecimalField(label=_("Refund Tax"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())

    refund_credit_net = forms.DecimalField(label=_("Apply Net"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())
    refund_credit_tax = forms.DecimalField(label=_("Apply Tax"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoiced_value = self.initial['job'].account.invoiced_total.gross
        self.payments_value = self.initial['job'].account.received_total.gross * -1
        self.overpaid_value = max(D('0.00'), self.payments_value - self.invoiced_value)
        self.underpaid_value = max(D('0.00'), self.invoiced_value - self.payments_value)
        if 'refund' in self.prefix:
            self.initial['amount'] = self.overpaid_value
        self.amount_value = convert_field_to_value(self['amount'])

        if self.billable_amount.gross < self.paid_amount.gross:
            refund = self.paid_amount - self.billable_amount
            self.initial['refund_net'] = refund.net
            self.initial['refund_tax'] = refund.tax
            if refund.gross > (self.initial['adjustment_net']+self.initial['adjustment_net']):
                self.initial['adjustment_net'] = D('0.00')
                self.initial['adjustment_tax'] = D('0.00')
            else:
                self.initial['adjustment_net'] -= refund.net
                self.initial['adjustment_tax'] -= refund.tax

    def consume_refund(self, refund):
        if self.billable_amount.gross > self.paid_amount.gross:
            consumable = self.billable_amount - self.paid_amount
            if refund.gross < consumable.gross:
                consumable = refund
            self.initial['refund_credit_net'] = consumable.net
            self.initial['refund_credit_tax'] = consumable.tax
            self.refund_credit_amount = consumable
            refund -= consumable
        return refund

    def clean(self):
        if 'refund' in self.prefix:
            if self.cleaned_data['amount'] > self.payments_value:
                self.add_error('amount', ValidationError(_("Cannot refund more than has been paid.")))


RefundFormSet = formset_factory(RefundRowForm, formset=BaseRefundFormSet, extra=0)


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name']


class BankAccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name']

    def __init__(self, *args, instance=None, **kwargs):
        if instance is None:  # create form
            banks = Account.objects.banks().order_by('-code')
            if banks.exists():
                next_code = int(banks.first().code) + 1
            else:
                next_code = BANK_CODE_RANGE[0]

            if next_code <= BANK_CODE_RANGE[1]:
                # set initial only if we were able to compute code within range
                kwargs['initial'] = {'code': str(next_code)}

            kwargs['instance'] = Account(account_type=Account.ASSET, asset_type=Account.BANK)
        else:
            kwargs['instance'] = instance

        super(BankAccountForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']

        if not code.isdigit() or \
                        int(code) < BANK_CODE_RANGE[0] or \
                        int(code) > BANK_CODE_RANGE[1]:
            raise ValidationError(_("Account code must be a number between %(min)s and %(max)s inclusive."),
                                  code='invalid', params={'min': BANK_CODE_RANGE[0], 'max': BANK_CODE_RANGE[1]})

        return code
