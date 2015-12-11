from datetime import date
from decimal import Decimal, InvalidOperation
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.forms import Form, ModelForm, ValidationError
from django.db.transaction import atomic
from django import forms
from systori.lib.fields import LocalizedDecimalField
from systori.lib.accounting.tools import compute_gross_tax, extract_net_tax
from ..task.models import Job
from .workflow import Account, credit_jobs, debit_jobs
from .constants import TAX_RATE, BANK_CODE_RANGE
from .models import Entry


class PaymentForm(Form):
    bank_account = forms.ModelChoiceField(label=_("Bank Account"), queryset=Account.objects.banks())
    amount = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=4)
    transacted_on = forms.DateField(label=_("Received Date"), initial=date.today, localize=True)


class SplitPaymentForm(Form):
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.all(), widget=forms.HiddenInput())
    amount = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=4, required=False)
    discount = forms.TypedChoiceField(
        label=_('Is discounted?'),
        coerce=Decimal,
        choices=[
            ('0', _('No discount applied')),
            ('0.02', _('2%')),
            ('0.03', _('3%')),
            ('0.1', _('10%')),
        ]
    )


class BaseSplitPaymentFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, prefix='split', initial=[{'job': job} for job in kwargs.pop('jobs', [])], **kwargs)
        self.payment_form = PaymentForm(*args, **kwargs)

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
            raise forms.ValidationError(_("The sum of splits must equal the payment amount."))

    def get_splits(self):
        splits = []
        for split in self.forms:
            if split.cleaned_data['amount']:
                job = split.cleaned_data['job']
                amount = split.cleaned_data['amount']
                discount = split.cleaned_data['discount']
                splits.append((job, amount, discount))
        return splits

    def save(self):
        credit_jobs(
            self.get_splits(),
            self.payment_form.cleaned_data['amount'],
            self.payment_form.cleaned_data['transacted_on'],
            self.payment_form.cleaned_data['bank_account']
        )

SplitPaymentFormSet = formset_factory(SplitPaymentForm, formset=BaseSplitPaymentFormSet, extra=0)


class DebitForm(Form):
    """ Represents a debit line for a single job/receivables account on an invoice form. """

    is_invoiced = forms.BooleanField(initial=True, required=False)
    job = forms.ModelChoiceField(queryset=Job.objects.none(), widget=forms.HiddenInput())
    amount_net = LocalizedDecimalField(initial=Decimal(0.0), max_digits=14, decimal_places=2, required=False)
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

        self.latest_estimate_net = self.job.estimate_total
        self.latest_itemized_net = self.job.billable_total
        self.latest_percent_complete = 0
        if self.latest_estimate_net > 0:
            self.latest_percent_complete = round((self.latest_itemized_net / self.latest_estimate_net) * 100, 2)

        try:
            amount_net_value = self['amount_net'].value()
            original_debit_amount_net = self['amount_net'].field.to_python(amount_net_value)
            if original_debit_amount_net is None:
                original_debit_amount_net = Decimal('0.00')
        except:
            original_debit_amount_net = Decimal('0.00')

        self.debit_amount_net = original_debit_amount_net
        self.debit_amount_gross = compute_gross_tax(original_debit_amount_net, TAX_RATE)[0]

        if self.initial['is_booked']:
            # accounting system already has the 'new' amounts since this invoice was booked
            self.new_debited_net, self.new_debited_tax, self.new_debited_gross = self.job.account.debits().net_tax_gross
            self.new_balance_net, self.new_balance_tax, self.new_balance_gross = self.job.account.balance_net_tax_gross

            # we need to undo the booking to get the 'base' amounts
            self.base_debited_net = self.new_debited_net - self.debit_amount_net
            self.base_debited_gross = self.new_debited_gross - self.debit_amount_gross
            self.base_balance_net = self.new_balance_net - self.debit_amount_net
            self.base_balance_gross = self.new_balance_gross - self.debit_amount_gross

        else:
            # no transactions exist yet so the account balance and debits don't include this new debit
            # accounting system has the 'base' amounts
            self.base_debited_net, self.base_debited_tax, self.base_debited_gross = self.job.account.debits().net_tax_gross
            self.base_balance_net, self.base_balance_tax, self.base_balance_gross = self.job.account.balance_net_tax_gross

        # subtract the net of all previous debits from all work completed to get amount not yet debited
        possible_debit_net = self.latest_itemized_net - self.base_debited_net
        if possible_debit_net > 0:
            self.billable_amount_net = possible_debit_net
            self.billable_amount_gross = compute_gross_tax(possible_debit_net, TAX_RATE)[0]
        else:
            self.billable_amount_net = Decimal('0.00')
            self.billable_amount_gross = Decimal('0.00')

        if str(self['is_override'].value()) == 'False':
            self.debit_amount_net = self.initial['amount_net'] = self.billable_amount_net
            self.debit_amount_gross = self.billable_amount_gross

        self.debit_amount_tax = self.debit_amount_gross - self.debit_amount_net

        # now that we know the correct debit amount we can calculate what the new balance will be
        self.new_debited_gross = self.base_debited_gross + self.debit_amount_gross
        self.new_debited_net = self.base_debited_net + self.debit_amount_net
        self.new_debited_tax = self.new_debited_gross + self.new_debited_net
        self.new_balance_gross = self.base_balance_gross + self.debit_amount_gross
        self.new_balance_net = self.base_balance_net + self.debit_amount_net
        self.new_balance_tax = self.new_balance_gross + self.new_balance_net

        if self.initial['is_booked']:
            # previous values come from json, could be different from latest values
            self.previous_debited_gross = Decimal(str(self.initial['debited_gross']))
            self.previous_balance_gross = Decimal(str(self.initial['balance_gross']))
            self.previous_estimate_net = Decimal(str(self.initial['estimate_net']))
            self.previous_itemized_net = Decimal(str(self.initial['itemized_net']))
        else:
            # latest and previous are the same when there is nothing booked yet
            self.previous_debited_gross = self.new_debited_gross
            self.previous_balance_gross = self.new_balance_gross
            self.previous_estimate_net = self.latest_estimate_net
            self.previous_itemized_net = self.latest_itemized_net

        # used to show user what has changed since last time invoice was created/edited
        self.diff_debited_gross = self.new_debited_gross - self.previous_debited_gross
        self.diff_balance_gross = self.new_balance_gross - self.previous_balance_gross
        self.diff_estimate_net = self.latest_estimate_net - self.previous_estimate_net
        self.diff_itemized_net = self.latest_itemized_net - self.previous_itemized_net
        self.diff_debit_amount_net = self.debit_amount_net - original_debit_amount_net

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
            'amount_net': self.debit_amount_net,
            'amount_gross': self.debit_amount_gross,
            'amount_tax': self.debit_amount_tax,
            'is_override': self.cleaned_data['is_override'],
            'override_comment': self.cleaned_data['override_comment'],
            'debited_gross': self.new_debited_gross,
            'debited_net': self.new_debited_net,
            'debited_tax': self.new_debited_tax,
            'balance_gross': self.new_balance_gross,
            'balance_net': self.new_balance_net,
            'balance_tax': self.new_balance_tax,
            'estimate_net': self.latest_estimate_net,
            'itemized_net': self.latest_itemized_net,
        }


class BaseDebitTransactionForm(BaseFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, prefix='job', **kwargs)
        self.estimate_net_total = Decimal('0.00')
        self.itemized_net_total = Decimal('0.00')
        self.debit_gross_total = Decimal('0.00')
        self.debit_net_total = Decimal('0.00')
        self.debited_gross_total = Decimal('0.00')
        self.debited_net_total = Decimal('0.00')
        self.balance_gross_total = Decimal('0.00')
        self.balance_net_total = Decimal('0.00')
        for form in self.forms:
            if form['is_invoiced'].value():
                self.estimate_net_total += form.latest_estimate_net
                self.itemized_net_total += form.latest_itemized_net
                self.debit_net_total += form.debit_amount_net
                self.debit_gross_total += form.debit_amount_gross
                self.debited_gross_total += form.new_debited_gross
                self.debited_net_total += form.new_debited_net
                self.balance_gross_total += form.new_balance_gross
                self.balance_net_total += form.new_balance_net

    def get_data(self):

        return {
            'debits': self.debits,

            'debit_gross': self.debit_gross_total,
            'debit_net': self.debit_net_total,
            'debit_tax': self.debit_gross_total - self.debit_net_total,

            'debited_gross': self.debited_gross_total,
            'debited_net': self.debited_gross_total,
            'debited_tax': self.debited_gross_total - self.debited_net_total,

            'balance_gross': self.balance_gross_total,
            'balance_net': self.balance_net_total,
            'balance_tax': self.balance_gross_total - self.balance_net_total
        }

    def save_debits(self, recognize_revenue=False):

        self.debits = []
        for debit_form in self.forms:
            if debit_form.cleaned_data['is_invoiced']:
                self.debits.append(debit_form.get_initial())

        skr03_debits = [(debit['job'], debit['amount_gross'], Entry.FLAT_DEBIT if debit['is_override'] else Entry.WORK_DEBIT) for debit in self.debits]
        transaction = debit_jobs(skr03_debits, recognize_revenue=recognize_revenue)

        return transaction


DebitTransactionFormSet = formset_factory(DebitForm, formset=BaseDebitTransactionForm, extra=0)


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
