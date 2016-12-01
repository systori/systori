from django.utils.translation import ugettext_lazy as _
from django.db import models, IntegrityError
from django.db.models.manager import BaseManager
from datetime import date
from decimal import Decimal
from .constants import *

from systori.lib.accounting.models import BaseAccount, BaseTransaction, BaseEntry
from ..task.models import Job


def create_account_for_job(job):
    """ Job passed to this function should have already been saved because
        an job.id is required to generate the account code. This function returns
        the newly created Account object.
    """
    # TODO: Add support for recycling account numbers when the maximum has been reached.
    from .workflow import DEBTOR_CODE_RANGE

    int(job.id)  # raises exception if id is not an int (eg. job hasn't been saved()'ed yet)
    code = DEBTOR_CODE_RANGE[0] + job.id
    if Account.objects.filter(code=str(code)).exists():
        raise IntegrityError("Account with code %s already exists." % code)
    if code > DEBTOR_CODE_RANGE[1]:
        raise ValueError("Account id %s is outside the maximum range of %s." % (code, DEBTOR_CODE_RANGE[1]))
    return Account.objects.create(account_type=Account.ASSET, asset_type=Account.RECEIVABLE, code=str(code))


class Account(BaseAccount):
    pass


class Entry(BaseEntry):
    job = models.ForeignKey('task.Job', models.SET_NULL, null=True, related_name="+")


class Transaction(BaseTransaction):
    entry_class = Entry
    account_class = Account
