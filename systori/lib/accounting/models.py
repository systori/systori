from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.manager import BaseManager
from datetime import date
from decimal import Decimal


def BaseAccount():

    class BaseAccountClass(models.Model):
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

    return BaseAccountClass


def BaseTransaction(Entry):

    class BaseTransactionClass(models.Model):
        """ A transaction is a collection of accounting entries (usually
            at least two entries to two different accounts).
        """
        recorded_on = models.DateTimeField(_("Date Recorded"), auto_now_add=True)
        notes = models.TextField(blank=True)

        class Meta:
            abstract = True

        def __init__(self, *args, **kwargs):
            super(BaseTransactionClass, self).__init__(*args, **kwargs)
            self._entries = []

        def debit(self, account, amount, **kwargs):
            entry = Entry(account=account, amount=account.as_debit(amount), **kwargs)
            self._entries.append(('debit', entry))
            return entry

        def credit(self, account, amount, **kwargs):
            entry = Entry(account=account, amount=account.as_credit(amount), **kwargs)
            self._entries.append(('credit', entry))
            return entry

        def _total(self, column):
            return sum([abs(item[1].amount) for item in self._entries if item[0] == column])

        @property
        def is_balanced(self):
            return self._total('debit') == self._total('credit')

        def save(self):
            assert self.is_balanced, "{} != {}".format(self._total('debit'), self._total('credit'))
            super(BaseTransactionClass, self).save()
            for item in self._entries:
                item[1].transaction = self
                item[1].save()

        @property
        def is_reconciled(self):
            return self.entries.filter(is_reconciled=True).exists()

    return BaseTransactionClass


class EntryQuerySet(models.QuerySet):
    @property
    def total(self):
        amount = Decimal(0.0)
        for entry in self:
            amount += entry.amount
        return amount


class EntryManager(BaseManager.from_queryset(EntryQuerySet)):
    use_for_related_fields = True


def BaseEntry():

    class BaseEntryClass(models.Model):
        """ Represents a debit or credit to an account. """

        transaction = models.ForeignKey('Transaction', related_name="entries")
        account = models.ForeignKey('Account', related_name="entries")

        amount = models.DecimalField(_("Amount"), max_digits=14, decimal_places=4, default=0.0)

        is_payment = models.BooleanField(_("Payment"), default=False)
        received_on = models.DateField(_("Date Received"), default=date.today)

        is_discount = models.BooleanField(_("Discount"), default=False)

        is_reconciled = models.BooleanField(_("Reconciled"), default=False)

        objects = EntryManager()

        def is_credit(self):
            return self.account.is_credit_amount(self.amount)

        def is_debit(self):
            return self.account.is_debit_amount(self.amount)

        def absolute_amount(self):
            return abs(self.amount)

        class Meta:
            abstract = True
            ordering = ['transaction__recorded_on', 'id']

    return BaseEntryClass
