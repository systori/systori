from django.utils.translation import ugettext_lazy as _
from ..project.models import Project
from django.db import models
from datetime import date
from decimal import Decimal


class Account(models.Model):
    """
                 Debit Credit
          Asset:   +     -
    Liabilities:   -     +
         Income:   -     +
       Expenses:   +     -
        Capital:   -     +
    
    http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
    """

    ASSET = "asset"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"
    CAPITAL = "capital"
    
    ACCOUNT_TYPE = (
        (ASSET, _("Asset")),
        (LIABILITY, _("Liability")),
        (INCOME, _("Income")),
        (EXPENSE, _("Expense")),
        (CAPITAL, _("Capital")),
    )
    account_type = models.CharField(_('Account Type'), max_length=128, choices=ACCOUNT_TYPE)
    code = models.CharField(_('Code'), max_length=32)

    @property
    def balance(self):
        amount = Decimal(0.0)
        for entry in self.entries.all():
            amount += entry.amount
        return amount

    @property
    def debits_total(self):
        amount = Decimal(0.0)
        for entry in self.entries.all():
            if (self.account_type in self.DEBIT_ACCOUNTS and entry.amount > 0) or
               (self.account_type in self.CREDITS_ACCOUNTS and entry.amount < 0):
                amount += entry.amount
        return amount

    @property
    def credits_total(self):
        amount = Decimal(0.0)
        for entry in self.entries.all():
            if (self.account_type in self.CREDITS_ACCOUNTS and entry.amount > 0) or
               (self.account_type in self.DEBIT_ACCOUNTS and entry.amount < 0):
                amount += entry.amount
        return amount

    DEBIT_ACCOUNTS  = (ASSET, EXPENSE)

    def debit(self, amount):
        if self.account_type in self.DEBIT_ACCOUNTS:
            return amount
        else:
            return amount * -1

    CREDIT_ACCOUNTS = (LIABILITY, INCOME, CAPITAL)

    def credit(self, amount):
        if self.account_type in self.CREDIT_ACCOUNTS:
            return amount
        else:
            return amount * -1


class Transaction(models.Model):
    """ A transaction is a collection of accounting entries (usually
        at least two entries to two different accounts).

        Difference between all credits and debits in a Transaction should always equal 0, this
        is the essence of double entry accounting.
    """
    date_recorded = models.DateTimeField(_("Date Recorded"), auto_now_add=True)
    notes = models.TextField(blank=True)

    def __init__(self):
        super(Transaction, self).__init__()
        self._entries = []

    def debit(self, account, amount):
        entry = Entry(account = account, amount = account.debit(amount))
        self._entries.append(('debit', entry))

    def credit(self, account, amount):
        entry = Entry(account = account, amount = account.credit(amount))
        self._entries.append(('credit', entry))
    
    def _total(self, column):
        return sum([abs(item[1].amount) for item in self._entries if item[0] == column])

    @property
    def is_balanced(self):
        return self._total('debit') == self._total('credit')

    def save(self):
        assert self.is_balanced
        super(Transaction, self).save()
        for item in self._entries:
            item[1].transaction = self
            item[1].save()


class Entry(models.Model):
    """ Represents a debit or credit to an account. """
    transaction = models.ForeignKey(Transaction, related_name="entries")
    account = models.ForeignKey(Account, related_name="entries")
    amount = models.DecimalField(_("Amount"), max_digits=14, decimal_places=4, default=0.0)

    class Meta:
        ordering = ['transaction__date_recorded']


class Payment(models.Model):
    """ Payment adds some extra information to a transaction with details on
        customer payments, such as when it was sent, received, etc.
    """
    transaction = models.ForeignKey(Transaction, related_name="payments")

    # Amount of payment
    amount = models.DecimalField(_("Amount"), max_digits=14, decimal_places=4, default=0.0)

    # Date customer wrote the check/initiated payment.
    date_sent = models.DateField(_("Date Sent"), default=date.today)

    # Date payment was settled/received.
    date_received = models.DateField(_("Date Received"), default=date.today)

    # Record whether discount was applied.
    is_discounted = models.BooleanField(_("Was discounted applied?"), default=False)