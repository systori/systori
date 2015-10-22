from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
from django.db.models.manager import BaseManager
from datetime import date
from decimal import Decimal


class BaseAccount(models.Model):
    """
                 Debit Credit
          Asset:   +     -
    Liabilities:   -     +
         Income:   -     +
       Expenses:   +     -

    http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
    """

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
    account_type = models.CharField(_('Account Type'), max_length=32, choices=ACCOUNT_TYPE)
    code = models.CharField(_('Code'), max_length=32)
    name = models.CharField(_('Name'), max_length=512, blank=True)

    class Meta:
        abstract = True
        ordering = ['code']

    def __str__(self):
        return '{} - {}'.format(self.code, self.name)

    @property
    def balance(self):
        return self.entries.all().total

    DEBIT_ACCOUNTS = (ASSET, EXPENSE)

    @property
    def is_debit_account(self):
        return self.account_type in self.DEBIT_ACCOUNTS

    CREDIT_ACCOUNTS = (LIABILITY, INCOME)

    @property
    def is_credit_account(self):
        return self.account_type in self.CREDIT_ACCOUNTS

    def as_debit(self, amount):
        """ Convert the 'amount' into correct positive/negative number based on double-entry accounting rules. """
        if self.is_debit_account:
            return amount
        else:
            return amount * -1

    def is_debit_amount(self, amount):
        if (self.is_debit_account and amount > 0) or \
                (self.is_credit_account and amount < 0):
            return True
        else:
            return False

    def as_credit(self, amount):
        """ Convert the 'amount' into correct positive/negative number based on double-entry accounting rules. """
        if self.is_credit_account:
            return amount
        else:
            return amount * -1

    def is_credit_amount(self, amount):
        if (self.is_debit_account and amount < 0) or \
                (self.is_credit_account and amount > 0):
            return True
        else:
            return False

    def debits(self):
        """ Get all debit entries for this account. """
        if self.is_debit_account:
            return self.entries.filter(amount__gt=0)
        else:
            return self.entries.filter(amount__lt=0)

    def credits(self):
        """ Get all credit entries for this account. """
        if self.is_credit_account:
            return self.entries.filter(amount__gt=0)
        else:
            return self.entries.filter(amount__lt=0)


class BaseTransaction(models.Model):
    """ A transaction is a collection of accounting entries (usually
        at least two entries to two different accounts).
    """
    entry_class = None  # Must be defined in subclass.
    notes = models.TextField(blank=True)

    # when this transaction was entered into the system
    recorded_on = models.DateTimeField(_("Date Recorded"), auto_now_add=True)
    # for payments, this is when a payment is received
    received_on = models.DateField(_("Date Received"), default=date.today)

    # finalized transactions cannot be edited
    finalized_on = models.DateField(_("Date Finalized"), null=True)
    is_finalized = models.BooleanField(_("Finalized"), default=False)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(BaseTransaction, self).__init__(*args, **kwargs)
        self._entries = []

    def debit(self, account, amount, **kwargs):
        entry = self.entry_class(account=account, amount=account.as_debit(round(amount, 2)), **kwargs)
        self._entries.append(('debit', entry))
        return entry

    def credit(self, account, amount, **kwargs):
        entry = self.entry_class(account=account, amount=account.as_credit(round(amount, 2)), **kwargs)
        self._entries.append(('credit', entry))
        return entry

    def _total(self, column):
        return sum([abs(item[1].amount) for item in self._entries if item[0] == column])

    @property
    def is_balanced(self):
        return self._total('debit') == self._total('credit')

    @property
    def is_reconciled(self):
        return self.entries.filter(is_reconciled=True).exists()

    def save(self, **kwargs):
        assert self.is_balanced, "{} != {}".format(self._total('debit'), self._total('credit'))
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
    def total(self):
        amount = Decimal(0.0)
        for entry in self:
            amount += entry.amount
        return amount


class EntryManager(BaseManager.from_queryset(EntryQuerySet)):
    use_for_related_fields = True


class BaseEntry(models.Model):
    """ Represents a debit or credit to an account.
    """

    transaction = models.ForeignKey('Transaction', related_name="entries")
    account = models.ForeignKey('Account', related_name="entries")

    amount = models.DecimalField(_("Amount"), max_digits=14, decimal_places=2, default=0.0)

    PAYMENT = "payment"
    DISCOUNT = "discount"
    WORK_DEBIT = "work-debit"
    FLAT_DEBIT = "flat-debit"
    ADJUSTMENT = "adjustment"
    OTHER = "other"

    ENTRY_TYPE = (
        (PAYMENT, _("Payment")),
        (DISCOUNT, _("Discount")),
        (WORK_DEBIT, _("Work Debit")),
        (FLAT_DEBIT, _("Flat Debit")),
        (ADJUSTMENT, _("Adjustment")),
        (OTHER, _("Other")),
    )
    # entry_type is only useful in the context of a customer account
    # entries in all other accounts will just be of type 'other'
    entry_type = models.CharField(_('Entry Type'), max_length=32, choices=ENTRY_TYPE, default=OTHER)

    # for bank entries
    reconciled_on = models.DateField(_("Date Reconciled"), null=True)
    is_reconciled = models.BooleanField(_("Reconciled"), default=False)

    objects = EntryManager()

    class Meta:
        abstract = True
        ordering = ['transaction__recorded_on', 'id']

    def is_credit(self):
        return self.account.is_credit_amount(self.amount)

    def is_debit(self):
        return self.account.is_debit_amount(self.amount)

    def absolute_amount(self):
        return abs(self.amount)

    def reconcile(self):
        self.is_reconciled = True
        self.reconciled_on = timezone.now()
        self.save()
