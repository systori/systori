from decimal import Decimal
from .models import Transaction
from ..task.models import Job
from .constants import *


def _transaction_sort_key(txn):
    """
    If there are payments and invoices created on the same day
    we want to make sure to process the payments first and then
    the invoices. Otherwise the transaction history on an
    invoice will look like a drunk cow liked it, that's bad.
    :param txn:
    :return: sort key
    """
    txn_date = txn.transacted_on.isoformat()[:10]
    type_weight = '0' if txn.transaction_type == txn.PAYMENT else '1'
    txn_id = str(txn.id)  # sort multiple invoices on same day by primary key id
    return txn_date+type_weight+txn_id


def get_transactions_for_jobs(jobs, transacted_on_or_before=None):
    """
    :param jobs: limit transaction details to specific set of jobs
    :param transacted_on_or_before: limit transactions up to and including a certain date
    :return: serializable data structure
    """

    txns_query = Transaction.objects.filter(entries__job__in=jobs).distinct()
    if transacted_on_or_before:
        txns_query = txns_query.filter(transacted_on__lte=transacted_on_or_before)

    transactions = list(txns_query)
    transactions.sort(key=_transaction_sort_key)

    result = []
    running_balance = Decimal(0.0)
    for txn in transactions:

        txn_dict = {
            'id': txn.id,
            'type': txn.transaction_type,
            'date': txn.transacted_on,

            'gross': Decimal(0.0),
            'net': Decimal(0.0),
            'tax': Decimal(0.0),

            'jobs': {}
        }

        if txn.transaction_type in (txn.INVOICE, txn.FINAL_INVOICE):
            txn_dict.update({
                'invoice_id': txn.invoice.id,
                'invoice_amount': txn.invoice.amount,
                'invoice_status': txn.invoice.status,
                'invoice_title': txn.invoice.json['title']
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

            elif entry.account.code == SKR03_PARTIAL_PAYMENTS_CODE and\
                    not txn.transaction_type == txn.FINAL_INVOICE:
                # final invoice transaction zeros out the partial payments
                # so in this case entry.amount will be a big negative number
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

        if txn.transaction_type == txn.FINAL_INVOICE:
            # we calculate the net here because it's too difficult
            # to extract this from the final transaction entries
            # see earlier comment regarding SKR03_PARTIAL_PAYMENTS_CODE
            for job_dict in txn_dict['jobs'].values():
                job_dict['net'] = job_dict['gross'] - job_dict['tax']
                txn_dict['net'] += job_dict['net']

        running_balance += txn_dict['gross']
        txn_dict['balance'] = running_balance

        result.append(txn_dict)

    return result
