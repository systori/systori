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
from ..document.models import Invoice, Adjustment, Payment, Refund, DocumentTemplate, DocumentSettings
from ..document.type import invoice as invoice_lib
from ..document.type import refund as refund_lib
from ..document.type import adjustment as adjustment_lib


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
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
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
            setattr(self, total+'_total', Amount.zero())

        for form in self.formset:
            if condition(form):
                for total in totals:
                    total_amount = getattr(self, total+'_total')
                    form_amount = getattr(form, total+'_amount')
                    setattr(self, total+'_total', total_amount+form_amount)


class BaseDocumentFormSet(BaseFormSet):

    def __init__(self, *args, instance, jobs, **kwargs):
        super().__init__(*args, prefix='job', initial=self.get_initial(instance, jobs), **kwargs)

    @staticmethod
    def get_initial(instance, jobs):
        initial = []
        for job in jobs.all():
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


class DocumentRowForm(Form):
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = self.initial['job']
        self.fields['job'].queryset = self.initial.pop('jobs')

    @property
    def json(self):
        raise NotImplementedError()

    @property
    def transaction(self):
        raise NotImplementedError()


class InvoiceForm(DocumentForm):

    parent = forms.ModelChoiceField(queryset=Invoice.objects.none(), required=False, widget=forms.HiddenInput())

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
        fields = ['parent', 'doc_template', 'is_final', 'document_date', 'invoice_no', 'title', 'header', 'footer', 'add_terms', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formset_class=InvoiceFormSet, **kwargs)

        if hasattr(self.instance, 'parent'):
            self.fields['parent'].queryset = Invoice.objects.filter(id=self.instance.parent.id)

        if not self.initial.get('header', None) or not self.initial.get('footer', None):
            default_text = DocumentSettings.get_for_language(settings.LANGUAGE_CODE)
            if default_text and default_text.invoice_text:
                rendered = default_text.invoice_text.render(self.instance.project)
                self.initial['header'] = rendered['header']
                self.initial['footer'] = rendered['footer']

        self.calculate_totals([
            'latest_estimate',
            'latest_progress',
            'base_invoiced',
            'base_balance',
            'new_invoiced',
            'new_balance',
            'itemized',
            'debit',
        ], lambda form: form['is_invoiced'].value())

        self.latest_progress_total_percent = 0
        if self.latest_estimate_total.net > 0:
            self.latest_progress_total_percent = round(self.latest_progress_total.net / self.latest_estimate_total.net * 100)

        self.base_invoiced_total_percent = 0
        if self.latest_progress_total.net > 0:
            self.base_invoiced_total_percent = round(self.base_invoiced_total.net / self.latest_progress_total.net * 100)

    @atomic
    def save(self, commit=True):

        invoice = self.instance
        data = self.cleaned_data
        data['jobs'] = self.formset.get_json_rows()

        if invoice.transaction:
            invoice.transaction.delete()

        invoice.transaction = debit_jobs(self.formset.get_transaction_rows(), recognize_revenue=data['is_final'])

        doc_settings = DocumentSettings.get_for_language(get_language())
        invoice.json = invoice_lib.serialize(invoice, data)
        invoice.letterhead = doc_settings.invoice_letterhead
        invoice.save(commit)


class InvoiceRowForm(DocumentRowForm):

    is_invoiced = forms.BooleanField(initial=False, required=False)

    debit_net = LocalizedDecimalField(label=_("Debit Net"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)
    debit_tax = LocalizedDecimalField(label=_("Debit Tax"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)

    is_override = forms.BooleanField(initial=False, required=False, widget=forms.HiddenInput())
    override_comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        comment_attrs = self.fields['override_comment'].widget.attrs
        comment_attrs['class'] = 'job-override-comment form-control'
        del comment_attrs['cols']
        del comment_attrs['rows']

        self.latest_estimate_amount = Amount.from_net(self.job.estimate_total, TAX_RATE)
        self.latest_progress_amount = Amount.from_net(self.job.progress_total, TAX_RATE)
        self.latest_progress_percent = self.job.progress_percent

        # previously saved debit or zero
        debit = initial_debit = self.initial.get('debit', Amount.zero())

        if 'is_booked' in self.initial:
            # accounting system already has the 'new' amounts since this invoice was booked
            self.new_invoiced_amount = self.job.account.invoiced
            self.new_balance_amount = self.job.account.balance

            # we need to undo the booking to get the 'base' amounts
            self.base_invoiced_amount = self.new_invoiced_amount - initial_debit
            self.base_balance_amount = self.new_balance_amount - initial_debit

        else:
            # no transactions exist yet so the account balance and debits don't include this new debit
            # accounting system has the 'base' amounts
            self.base_invoiced_amount = self.job.account.invoiced
            self.base_balance_amount = self.job.account.balance

        self.base_invoiced_percent = 0
        if self.latest_progress_amount.net > 0:
            self.base_invoiced_percent = round(self.base_invoiced_amount.net / self.latest_progress_amount.net * 100)

        # subtract already invoiced from potentially billable to get amount not yet invoiced
        self.itemized_amount = self.latest_progress_amount - self.base_invoiced_amount
        if self.itemized_amount.gross < 0:
            self.itemized_amount = Amount.zero()

        if str(self['is_override'].value()) == 'False':
            if self.itemized_amount.net > 0:
                debit = self.itemized_amount

        self.initial['debit_net'] = debit.net
        self.initial['debit_tax'] = debit.tax

        self.debit_amount = Amount(
            convert_field_to_value(self['debit_net']),
            convert_field_to_value(self['debit_tax'])
        )

        # now that we know the correct debit amount we can calculate what the new balance will be
        self.new_invoiced_amount = self.base_invoiced_amount + self.debit_amount
        self.new_balance_amount = self.base_balance_amount + self.debit_amount

        self.new_invoiced_percent = 0
        if self.latest_estimate_amount.net > 0:
            if self.new_invoiced_amount.net >= self.latest_estimate_amount.net:
                self.new_invoiced_percent = 100
            else:
                self.new_invoiced_percent = round((self.new_invoiced_amount.net / self.latest_estimate_amount.net) * 100, 2)

        if 'is_booked' in self.initial:
            # previous values come from json, could be different from latest values
            self.previous_invoiced_amount = self.initial['invoiced']
            self.previous_balance_amount = self.initial['balance']
            self.previous_estimate_amount = self.initial['estimate']
            self.previous_progress_amount = self.initial['progress']
        else:
            # latest and previous are the same when there is nothing booked yet
            self.previous_invoiced_amount = self.new_invoiced_amount
            self.previous_balance_amount = self.new_balance_amount
            self.previous_estimate_amount = self.latest_estimate_amount
            self.previous_progress_amount = self.latest_progress_amount

        # used to show user what has changed since last time invoice was created/edited
        self.diff_invoiced_amount = self.new_invoiced_amount - self.previous_invoiced_amount
        self.diff_balance_amount = self.new_balance_amount - self.previous_balance_amount
        self.diff_estimate_amount = self.latest_estimate_amount - self.previous_estimate_amount
        self.diff_progress_amount = self.latest_progress_amount - self.previous_progress_amount
        self.diff_debit_amount = self.debit_amount - initial_debit

    def clean(self):
        if self.cleaned_data['is_override'] and \
                        len(self.cleaned_data['override_comment']) < 1:
            self.add_error('override_comment',
                           ValidationError(_("A comment is required for flat invoice.")))

    @property
    def json(self):
        if self.cleaned_data['is_invoiced']:
            return {
                'job': self.job,
                'is_invoiced': True,
                'debit': self.debit_amount,
                'is_override': self.cleaned_data['is_override'],
                'override_comment': self.cleaned_data['override_comment'],
                'invoiced': self.new_invoiced_amount,
                'balance': self.new_balance_amount,
                'estimate': self.latest_estimate_amount,
                'progress': self.latest_progress_amount,
            }

    @property
    def transaction(self):
        if self.cleaned_data['is_invoiced']:
            debit_type = Entry.WORK_DEBIT
            if self.cleaned_data['is_override']:
                debit_type = Entry.FLAT_DEBIT
            if self.debit_amount.gross > 0:
                return self.job, self.debit_amount, debit_type


InvoiceFormSet = formset_factory(InvoiceRowForm, formset=BaseDocumentFormSet, extra=0)


class AdjustmentForm(DocumentForm):
    invoice = forms.ModelChoiceField(label=_("Invoice"), queryset=Invoice.objects.all(), widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Adjustment
        fields = ['invoice']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formset_class=AdjustmentFormSet, **kwargs)
        self.calculate_totals([
            'paid',
            'invoiced',
            'invoiced_diff',
            'progress',
            'progress_diff',
            'adjustment',
            'corrected',
        ])

    @atomic
    def save(self, commit=True):

        adjustment = self.instance

        if adjustment.transaction:
            adjustment.transaction.delete()

        adjustment.transaction = adjust_jobs(self.formset.get_adjustments())

        doc_settings = DocumentSettings.get_for_language(get_language())

        adjustment.letterhead = doc_settings.invoice_letterhead
        adjustment.json = adjustment_lib.serialize(adjustment, {})
        adjustment.save(commit)


class AdjustmentRowForm(DocumentRowForm):

    adjustment_net = LocalizedDecimalField(label=_("Adjustment Net"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)
    adjustment_tax = LocalizedDecimalField(label=_("Adjustment Tax"), initial=D('0.00'), max_digits=14, decimal_places=2, required=False)

    corrected_net = LocalizedDecimalField(label=_("Corrected Net"), max_digits=14, decimal_places=2, required=False)
    corrected_tax = LocalizedDecimalField(label=_("Corrected Tax"), max_digits=14, decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Paid Column
        self.paid_amount = self.job.account.paid.negate

        # Invoiced Column
        if 'invoiced' in self.initial:
            self.invoiced_amount = self.initial['invoiced']
        else:
            self.invoiced_amount = self.job.account.invoiced
        self.invoiced_diff_amount = self.invoiced_amount - self.paid_amount

        # Billable Column
        self.progress_amount = Amount.from_net(self.job.progress_total, TAX_RATE)
        self.progress_diff_amount = self.progress_amount - self.invoiced_amount

        # Adjustment Column
        self.adjustment_amount = Amount(
            convert_field_to_value(self['adjustment_net']),
            convert_field_to_value(self['adjustment_tax'])
        )

        # Corrected Column
        self.initial['corrected_net'] = self.invoiced_amount.net
        self.initial['corrected_tax'] = self.invoiced_amount.tax
        self.corrected_amount = Amount(
            convert_field_to_value(self['corrected_net']),
            convert_field_to_value(self['corrected_tax'])
        )

    def clean(self):
        pass
        #if self.adjustment_amount.gross > self.invoiced_amount.gross:
        #    self.add_error('adjustment_net', ValidationError(_("Adjustment cannot be greater than invoiced amount.")))


AdjustmentFormSet = formset_factory(AdjustmentRowForm, formset=BaseDocumentFormSet, extra=0)


class PaymentForm(DocumentForm):
    transacted_on = forms.DateField(label=_("Received Date"), initial=date.today, localize=True)
    invoice = forms.ModelChoiceField(label=_("Invoice"), queryset=Invoice.objects.all(), widget=forms.HiddenInput(), required=False)
    bank_account = forms.ModelChoiceField(label=_("Bank Account"), queryset=Account.objects.banks())
    amount = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=4)
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
        fields = [
            'transacted_on', 'invoice',
            'bank_account', 'amount', 'discount',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formset_class=PaymentFormSet, **kwargs)
        self.amount_value = Amount.from_gross(convert_field_to_value(self['amount']), TAX_RATE)
        self.calculate_totals([
            'balance',
            'payment',
            'discount',
            'credit'
        ])

    def clean(self):
        splits = Amount.zero()
        for form in self.formset:
            splits += form.payment_amount
        if splits.gross != self.amount_value.gross:
            raise forms.ValidationError(_("The sum of splits must equal the payment amount."))

    @atomic
    def save(self, commit=True):
        credit_jobs(
            self.get_splits(),
            self.payment_form.cleaned_data['amount'],
            self.payment_form.cleaned_data['transacted_on'],
            self.payment_form.cleaned_data['bank_account']
        )
        invoice = self.instance.invoice
        if invoice and not invoice.status == Invoice.PAID:
            invoice.pay()
            invoice.save()


class PaymentRowForm(DocumentRowForm):

    payment_net = LocalizedDecimalField(label=_("Amount Net"), max_digits=14, decimal_places=2, required=False)
    payment_tax = LocalizedDecimalField(label=_("Amount Tax"), max_digits=14, decimal_places=2, required=False)

    discount_net = LocalizedDecimalField(label=_("Discount Net"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())
    discount_tax = LocalizedDecimalField(label=_("Discount Tax"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for column_name in ['payment', 'discount']:
            net = convert_field_to_value(self[column_name+'_net'])
            tax = convert_field_to_value(self[column_name+'_tax'])
            setattr(self, column_name+'_amount', Amount(net, tax))

        if 'invoiced' in self.initial:
            self.balance_amount = self.initial['invoiced']
        else:
            self.balance_amount = self.job.account.balance

        self.credit_amount = self.payment_amount + self.discount_amount


PaymentFormSet = formset_factory(PaymentRowForm, formset=BaseDocumentFormSet, extra=0)


class RefundForm(DocumentForm):
    title = forms.CharField(label=_('Title'), initial=_("Refund"))
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    class Meta(DocumentForm.Meta):
        model = Refund
        fields = ['document_date', 'title', 'header', 'footer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formset_class=RefundFormSet, **kwargs)
        if len(jobs) <= 1:
            not_overpaid_jobs = []  # if there is only one job, no sense to allow applying to the same job
        else:
            not_overpaid_jobs = [form.initial['job'] for form in self.refund_jobs_form.forms if form.overpaid_value <= 0]
        self.apply_jobs_form = RefundFormSet(refund_total=self.refund_jobs_form.amount_total,
                                                prefix='apply', initial=self.get_initial(not_overpaid_jobs),
                                                **kwargs)
        self.refund_amount = self.refund_jobs_form.amount_total - self.apply_jobs_form.amount_total

        self.calculate_totals([
            'amount',
            'invoiced',
            'payments',
            'overpaid',
            'underpaid',
        ])

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

    @atomic
    def save(self, commit=True):

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


class RefundRowForm(DocumentRowForm):
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

        if self.progress_amount.gross < self.paid_amount.gross:
            refund = self.paid_amount - self.progress_amount
            self.initial['refund_net'] = refund.net
            self.initial['refund_tax'] = refund.tax
            if refund.gross > (self.initial['adjustment_net']+self.initial['adjustment_net']):
                self.initial['adjustment_net'] = D('0.00')
                self.initial['adjustment_tax'] = D('0.00')
            else:
                self.initial['adjustment_net'] -= refund.net
                self.initial['adjustment_tax'] -= refund.tax

    def consume_refund(self, refund):
        if self.progress_amount.gross > self.paid_amount.gross:
            consumable = self.progress_amount - self.paid_amount
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


RefundFormSet = formset_factory(RefundRowForm, formset=BaseDocumentFormSet, extra=0)


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
