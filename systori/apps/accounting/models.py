from django.utils.translation import ugettext_lazy as _
from ..project.models import Project
from django.db import models
from datetime import date
from decimal import Decimal


class Account(models.Model):
    """ At least two accounts are required to perform double entry accounting.
    """

    # bs - balance sheet, debit (+), credit (-)
    # pl - profit/loss, debit (-), credit (+)

    # Each project gets a receivable account.
    RECEIVABLE = "bs:receivable" # 10.001: debit (+) on invoice, credit (-) on payment

    # Business related accounts, one of each per installation of systori.
    SALES = "pl:sales" # 4000: credit (+) on invoice, debit (-) on payment

    BANK = "bs:bank"   # 1800: debit (+) on payment
    PAYMENTS = "pl:payments" # 3272: credit (+) on payment
    TAXES = "taxes" # credit (+) on payment

    ACCOUNT_TYPE = (
        (SALES, _("Sales - 4000")),
    )
    account_type = models.CharField(_('Account Type'), max_length=128)#, choices=ACCOUNT_TYPE)

    @property
    def balance(self):
        amount = Decimal(0.0)
        for entry in self.entries.all():
            amount += entry.amount
        return amount

    def credit(self, ):

class Transaction(models.Model):
    """ A transaction is a collection of accounting entries (usually
        at least two entries to two different accounts).

        An invoice will result in a Transaction with two entries:

          1. Negative amount entry for the construction company. (given away value)
          2. Positive amount entry for the customer. (received value)

        An invoice being paid will also result in two entries:

          1. Positive amount entry for construction company. (received payment for value)
          2. Negative amount entry for the customer. (paid for value)

        When construction company does work and sends an invoice
        they are negative at that moment (haven't gotten paid)
        and the customer is positive (they've gotten value). The
        customer must then settle the debt by making a payment and
        balancing the books.

        Sum of all entries in a Transaction should always equal 0, this
        is the essence of double entry accounting.
    """

    # Date customer wrote the check/initiated payment.
    date_sent = models.DateField(_("Date Sent"), default=date.today)

    # Date payment was settled/received.
    date_received = models.DateField(_("Date Received"), default=date.today)

    # Date this transaction was entered into systori.
    date_recorded = models.DateTimeField(_("Date Recorded"), auto_now_add=True)

    # Used to record payments. Especially since a single payment could cover multiple
    # projects the total amount of the payment would be entered here and the split/breakdown
    # towards each project would be entered in the entry.
    amount = models.DecimalField(_("Amount"), max_digits=14, decimal_places=4, default=0.0)

    notes = models.TextField(blank=True)


class Entry(models.Model):
    """ Represents a debit or credit to an account. """
    transaction = models.ForeignKey(Transaction, related_name="entries")
    account = models.ForeignKey(Account, related_name="entries")
    amount = models.DecimalField(_("Amount"), max_digits=14, decimal_places=4, default=0.0)

    class Meta:
        ordering = ['transaction__date_recorded']
