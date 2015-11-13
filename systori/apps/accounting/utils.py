from decimal import Decimal
from .models import Transaction
from ..task.models import Job
from .constants import *


def get_transactions_for_jobs(jobs, transacted_on_or_before=None):
    """
    :param jobs: limit transaction details to specific set of jobs
    :param transacted_on_or_before: limit transactions up to and including a certain date
    :return: serializable data structure
    """

    txns = Transaction.objects\
        .filter(entries__job__in=jobs)\
        .distinct()\
        .order_by('transacted_on')

    if transacted_on_or_before:
        txns = txns.filter(transacted_on__lte=transacted_on_or_before)

    result = []
    for txn in txns:

        txn_dict = {
            'id': txn.id,
            'type': txn.transaction_type,
            'date': txn.transacted_on,

            'gross': Decimal(0.0),
            'net': Decimal(0.0),
            'tax': Decimal(0.0),

            'jobs': {}
        }

        if txn.transaction_type == txn.INVOICE:
            txn_dict.update({
                'invoice_id': txn.invoice.id,
                'invoice_amount': txn.invoice.amount
            })

        elif txn.transaction_type == txn.PAYMENT:
            txn_dict.update({
                'is_reconciled': False,
                'payment_received': Decimal(0.0),  # actual amount received from customer
                'payment_applied': Decimal(0.0),  # part of payment applied to this set of 'jobs'
                'discount_applied': Decimal(0.0),  # discount applied to this set of 'jobs'
                # payment_applied + discount_applied = gross for this transaction
            })

        for entry in txn.entries.prefetch_related('job', 'account__job__project').all():

            if txn.transaction_type == txn.PAYMENT and entry.account.is_bank:
                txn_dict['is_reconciled'] = entry.is_reconciled
                txn_dict['payment_received'] = entry.amount * -1
                continue

            job = entry.job

            if job not in jobs:
                # skip jobs we're not interested in
                continue

            if job.id not in txn_dict['jobs']:
                txn_dict['jobs'][job.id] = {
                    'job.id': job.id,
                    'code': job.code,
                    'name': job.name,

                    'gross': Decimal(0.0),
                    'net': Decimal(0.0),
                    'tax': Decimal(0.0),

                    'entries': []
                }
                if txn.transaction_type == txn.PAYMENT:
                    txn_dict['jobs'][job.id].update({
                        'payment_applied': Decimal(0.0),
                        'discount_applied': Decimal(0.0),
                    })

            job_dict = txn_dict['jobs'][job.id]

            if entry.account.code == SKR03_TAX_PAYMENTS_CODE:
                txn_dict['tax'] += entry.amount
                job_dict['tax'] += entry.amount

            elif entry.account.code == SKR03_PARTIAL_PAYMENTS_CODE:
                txn_dict['net'] += entry.amount
                job_dict['net'] += entry.amount

            else:  # not tax or income entry, could be a job account entry

                try:

                    # this attribute access throws exception if this is not a job account entry
                    entry.account.job

                    # if we made it this far it means we're dealing with an entry to the job account

                    txn_dict['gross'] += entry.amount
                    job_dict['gross'] += entry.amount
                    job_dict['entries'].append(
                        {'type': entry.entry_type, 'amount': entry.amount}
                    )

                    # separate out payment vs discount credits
                    if entry.entry_type == entry.PAYMENT:
                        txn_dict['payment_applied'] += entry.amount
                        job_dict['payment_applied'] += entry.amount
                    elif entry.entry_type == entry.DISCOUNT:
                        txn_dict['discount_applied'] += entry.amount
                        job_dict['discount_applied'] += entry.amount

                except Job.DoesNotExist:
                    pass

        result.append(txn_dict)

    return result
