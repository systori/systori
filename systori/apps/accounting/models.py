from django.utils.translation import ugettext_lazy as _
from django.db import models, IntegrityError
from django.db.models.manager import BaseManager
from datetime import date
from decimal import Decimal
from .constants import *

from systori.lib.accounting.models import BaseAccount, BaseTransaction, BaseEntry


def create_account_for_job(job):
    """ Job passed to this function should have already been saved because
        an job.id is required to generate the account code. This function returns
        the newly created Account object.
    """
    # TODO: Add support for recycling account numbers when the maximum has been reached.
    from .skr03 import DEBTOR_CODE_RANGE

    int(job.id)  # raises exception if id is not an int (eg. job hasn't been saved()'ed yet)
    code = DEBTOR_CODE_RANGE[0] + job.id
    if Account.objects.filter(code=str(code)).exists():
        raise IntegrityError("Account with code %s already exists." % code)
    if code > DEBTOR_CODE_RANGE[1]:
        raise ValueError("Account id %s is outside the maximum range of %s." % (code, DEBTOR_CODE_RANGE[1]))
    return Account.objects.create(account_type=Account.ASSET, code=str(code))


class AccountQuerySet(models.QuerySet):
    def banks(self):
        return Account.objects.filter(account_type=Account.ASSET).filter(job__isnull=True)


class AccountManager(BaseManager.from_queryset(AccountQuerySet)):
    use_for_related_fields = True


class Account(BaseAccount()):
    objects = AccountManager()

    class Meta:
        ordering = ['code']

    def __str__(self):
        return '{} - {}'.format(self.code, self.name)

    @property
    def balance_base(self):
        return round(self.balance / (1 + TAX_RATE), 2)

    @property
    def balance_tax(self):
        return round(self.balance_base * TAX_RATE, 2)

    def payments(self):
        """ This method should only be used on customer accounts (trade debtors).
            It returns all credit entries marked as payment.
        """
        self.job  # Raises DoesNotExist exception if no job exists to prevent misuse of this method.
        return self.credits().filter(is_payment=True)

    def discounts(self):
        """ This method should only be used on customer accounts (trade debtors).
            It returns all credit entries marked as discount.
        """
        self.job  # Raises DoesNotExist exception if no job exists to prevent misuse of this method.
        return self.credits().filter(is_discount=True)


class Entry(BaseEntry()):
    """ Represents a debit or credit to an account. """

    @property
    def amount_base(self):
        return round(self.amount / (1 + TAX_RATE), 2)

    @property
    def amount_tax(self):
        return round(self.amount_base * TAX_RATE, 2)


class Transaction(BaseTransaction(Entry)):
    """ A transaction is a collection of accounting entries (usually
        at least two entries to two different accounts).
    """

    def discounts_to_account(self, account):
        return self.entries.filter(account=account).filter(is_discount=True)


