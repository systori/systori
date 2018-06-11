from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
from django.db.models.manager import BaseManager
from django.core.exceptions import ObjectDoesNotExist
from datetime import date

from .tools import Amount


class AccountQuerySet(models.QuerySet):
    def banks(self):
        return self.filter(asset_type=BaseAccount.BANK)


class AccountManager(BaseManager.from_queryset(AccountQuerySet)):
    use_for_related_fields = True


class BaseAccount(models.Model):
    """
                 Debit Credit
          Asset:   +     -
    Liabilities:   -     +
         Income:   -     +
       Expenses:   +     -

    http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
    """

    objects = AccountManager()

    # Account Type

    ASSET = "asset"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"

    ACCOUNT_TYPE = (
        (ASSET, _("Asset")),
        (LIABILITY, _("Liability")),
        (INCOME, _("Income")),
        (EXPENSE, _("Expense")),
    )
    account_type = models.CharField(
        _("Account Type"), max_length=32, choices=ACCOUNT_TYPE
    )

    # Asset Type (when account.account_type=ASSET)

    BANK = "bank"
    RECEIVABLE = "receivable"

    ASSET_TYPE = ((BANK, _("Bank")), (RECEIVABLE, _("Accounts Receivable")))
    asset_type = models.CharField(
        _("Asset Type"), null=True, max_length=32, choices=ASSET_TYPE
    )

    code = models.CharField(_("Code"), max_length=32)
    name = models.CharField(_("Name"), max_length=512, blank=True)

    class Meta:
        abstract = True
        ordering = ["code"]

    def __str__(self):
        return "{} - {}".format(self.code, self.name)

    @property
    def is_bank(self):
        return self.asset_type == self.BANK

    @property
    def is_receivable(self):
        return self.asset_type == self.RECEIVABLE

    @property
    def balance(self):
        return self.entries.all().sum

    @property
    def invoiced(self):
        """ all invoices minus any adjustments """
        return self.entries.all().invoice.sum

    @property
    def paid(self):
        """ all payments and discounts minus any refunds """
        return self.entries.all().payment.sum

    @property
    def debits(self):
        """ Get all debit entries for this account. """
        if self.is_debit_account:
            return self.entries.filter(value__gt=0)
        else:
            return self.entries.filter(value__lt=0)

    @property
    def credits(self):
        """ Get all credit entries for this account. """
        if self.is_credit_account:
            return self.entries.filter(value__gt=0)
        else:
            return self.entries.filter(value__lt=0)

    DEBIT_ACCOUNTS = (ASSET, EXPENSE)

    @property
    def is_debit_account(self):
        return self.account_type in self.DEBIT_ACCOUNTS

    CREDIT_ACCOUNTS = (LIABILITY, INCOME)

    @property
    def is_credit_account(self):
        return self.account_type in self.CREDIT_ACCOUNTS

    def as_debit(self, value):
        """ Convert the 'value' into correct positive/negative number based on double-entry accounting rules. """
        if self.is_debit_account:
            return value
        else:
            return value * -1

    def is_debit_value(self, value):
        if (self.is_debit_account and value > 0) or (
            self.is_credit_account and value < 0
        ):
            return True
        else:
            return False

    def as_credit(self, value):
        """ Convert the 'value' into correct positive/negative number based on double-entry accounting rules. """
        if self.is_credit_account:
            return value
        else:
            return value * -1

    def is_credit_value(self, value):
        if (self.is_debit_account and value < 0) or (
            self.is_credit_account and value > 0
        ):
            return True
        else:
            return False


class BaseTransaction(models.Model):
    """ A transaction is a collection of accounting entries (usually
        at least two entries to two different accounts).
    """

    entry_class = None  # Must be defined in subclass.
    account_class = None  # Must be defined in subclass.

    notes = models.TextField(blank=True)

    # this is when a payment is received or invoice is dated
    transacted_on = models.DateField(_("Date Transacted"), default=date.today)

    # finalized transactions cannot be edited
    finalized_on = models.DateField(_("Date Finalized"), null=True)
    is_finalized = models.BooleanField(_("Finalized"), default=False)

    # transaction marks the point in time when revenue became recognized
    is_revenue_recognized = models.BooleanField(default=False)

    # when this transaction was entered into the system
    recorded_on = models.DateTimeField(_("Date Recorded"), auto_now_add=True)

    INVOICE = "invoice"
    PAYMENT = "payment"
    ADJUSTMENT = "adjustment"
    REFUND = "refund"

    TRANSACTION_TYPE = (
        (INVOICE, _("Invoice")),
        (PAYMENT, _("Payment")),
        (ADJUSTMENT, _("Adjustment")),
        (REFUND, _("Refund")),
    )
    transaction_type = models.CharField(
        _("Transaction Type"), null=True, max_length=32, choices=TRANSACTION_TYPE
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(BaseTransaction, self).__init__(*args, **kwargs)
        self._entries = []

    def debit(self, account, value, **kwargs):
        assert value > 0
        if type(account) is str:
            account = self.account_class.objects.get(code=account)
        debit_value = account.as_debit(round(value, 2))
        entry = self.entry_class(account=account, value=debit_value, **kwargs)
        self._entries.append(("debit", entry))
        return entry

    def credit(self, account, value, **kwargs):
        assert value > 0
        if type(account) is str:
            account = self.account_class.objects.get(code=account)
        credit_value = account.as_credit(round(value, 2))
        entry = self.entry_class(account=account, value=credit_value, **kwargs)
        self._entries.append(("credit", entry))
        return entry

    def signed(self, account, signed_value, **kwargs):
        assert signed_value != 0
        if type(account) is str:
            account = self.account_class.objects.get(code=account)
        entry = self.entry_class(
            account=account, value=round(signed_value, 2), **kwargs
        )
        entry_type = "credit" if account.is_credit_value(signed_value) else "debit"
        self._entries.append((entry_type, entry))
        return entry

    def _total(self, column):
        return sum([abs(item[1].value) for item in self._entries if item[0] == column])

    def _show_table(self):
        from systori.lib.templatetags.customformatting import money

        for entry in self._entries:
            acct, value = entry[1].account, entry[1].value
            try:
                acct_name = acct.code + " " + acct.job.name
            except ObjectDoesNotExist:
                acct_name = acct.code + " " + acct.name
            if entry[0] == "debit":
                print(" {:<25} {:>10} {:>10}".format(acct_name, money(value), ""))
            else:
                print(" {:<25} {:>10} {:>10}".format(acct_name, "", money(value)))
        print(
            " {:>25} {:>10} {:>10}".format(
                "total:", money(self._total("debit")), money(self._total("credit"))
            )
        )

    @property
    def is_balanced(self):
        return self._total("debit") == self._total("credit")

    @property
    def is_reconciled(self):
        for entry in self.entries.all():
            if entry.is_reconciled:
                return True
        return False

    def save(self, debug=False, **kwargs):
        assert len(self._entries) == 0 or len(self._entries) >= 2
        if debug:
            self._show_table()
        assert self.is_balanced, "{} != {}".format(
            self._total("debit"), self._total("credit")
        )
        super().save(**kwargs)
        for item in self._entries:
            item[1].transaction = self
            item[1].save()

    def finalize(self):
        self.is_finalized = True
        self.finalized_on = timezone.now()
        self.save()


class EntryQuerySet(models.QuerySet):
    @property
    def invoice(self):
        """ Queryset of all debit entries - adjustments, sum of which is the total invoiced. """
        return self.filter(entry_type__in=BaseEntry.TYPES_FOR_INVOICED_SUM)

    @property
    def payment(self):
        """ Queryset of all credit entries - refunds, sum of which is the total collected cash. """
        return self.filter(entry_type__in=BaseEntry.TYPES_FOR_PAID_SUM)

    @property
    def sum(self):
        amount = Amount.zero()
        for entry in self:
            amount += entry.amount
        return amount


class EntryManager(BaseManager.from_queryset(EntryQuerySet)):
    use_for_related_fields = True


class BaseEntry(models.Model):
    """ Represents the tax, net or gross portion of a debit or credit to an account.
    """

    transaction = models.ForeignKey(
        "Transaction", related_name="entries", on_delete=models.CASCADE
    )
    account = models.ForeignKey(
        "Account", related_name="entries", on_delete=models.CASCADE
    )

    value = models.DecimalField(_("Value"), max_digits=14, decimal_places=2)

    # Entry Type

    # credits: decrease or pay down a customers debt
    PAYMENT = "payment"
    DISCOUNT = "discount"
    REFUND_CREDIT = "refund-credit"  # apply a refund from another job to this job
    PAYMENT_TYPES = (PAYMENT, DISCOUNT, REFUND_CREDIT)
    ADJUSTMENT = (
        "adjustment"
    )  # if customer is over-invoiced, this brings account back to billable

    # debits: increase the customers debt
    WORK_DEBIT = "work-debit"  # debit value calculated from completed tasks
    FLAT_DEBIT = "flat-debit"  # flat fee debit, not based on tasks
    DEBIT_TYPES = (WORK_DEBIT, FLAT_DEBIT)
    REFUND = (
        "refund"
    )  # if customer over-pays, this brings account back to what was invoiced or could be billed

    # If you take a sum of all TYPES_FOR_INVOICED_SUM entries you'll end up with the actual invoiced amount.
    TYPES_FOR_INVOICED_SUM = DEBIT_TYPES + (ADJUSTMENT,)

    # If you take a sum of all TYPES_FOR_PAID_SUM entries you'll end up with the total cash collected.
    TYPES_FOR_PAID_SUM = PAYMENT_TYPES + (REFUND,)

    OTHER = "other"

    ENTRY_TYPE = (
        (PAYMENT, _("Payment")),
        (REFUND_CREDIT, _("Refund Credit")),
        (DISCOUNT, _("Discount")),
        (WORK_DEBIT, _("Work Debit")),
        (FLAT_DEBIT, _("Flat Debit")),
        (REFUND, _("Refund")),
        (ADJUSTMENT, _("Adjustment")),
        (OTHER, _("Other")),
    )
    # entry_type is only useful in the context of a customer account
    # entries in all other accounts will just be of type 'other'
    entry_type = models.CharField(
        _("Entry Type"), max_length=32, choices=ENTRY_TYPE, default=OTHER
    )

    # Value Type

    NET = "net"
    TAX = "tax"
    GROSS = "gross"

    VALUE_TYPE = ((NET, _("Net")), (TAX, _("Tax")), (GROSS, _("Gross")))
    value_type = models.CharField(_("Value Type"), max_length=32, choices=VALUE_TYPE)

    # for bank entries
    reconciled_on = models.DateField(_("Date Reconciled"), null=True)
    is_reconciled = models.BooleanField(_("Reconciled"), default=False)

    objects = EntryManager()

    class Meta:
        abstract = True
        ordering = ["transaction__transacted_on", "id"]

    @property
    def is_credit(self):
        return self.account.is_credit_value(self.value)

    @property
    def is_debit(self):
        return self.account.is_debit_value(self.value)

    @property
    def is_net(self):
        return self.value_type == self.NET

    @property
    def is_tax(self):
        return self.value_type == self.TAX

    @property
    def is_gross(self):
        return self.value_type == self.GROSS

    @property
    def amount(self):
        return Amount.from_entry(self)

    def reconcile(self):
        self.is_reconciled = True
        self.reconciled_on = timezone.now()
        self.save()
