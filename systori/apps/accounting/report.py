from django.core.exceptions import ObjectDoesNotExist
from .models import Transaction
from systori.lib.accounting.tools import Amount


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


def create_payments_report(jobs, transacted_on_or_before=None):
    """
    :param jobs: limit transaction details to specific set of jobs
    :param transacted_on_or_before: limit transactions up to and including a certain date
    :return: serializable data structure
    """

    txns_query = Transaction.objects \
        .filter(entries__job__in=jobs) \
        .prefetch_related('entries__job__project') \
        .prefetch_related('entries__account') \
        .distinct()

    if transacted_on_or_before:
        txns_query = txns_query.filter(transacted_on__lte=transacted_on_or_before)

    transactions = list(txns_query)
    transactions.sort(key=_transaction_sort_key)

    report = {
        'invoiced': Amount.zero(),
        'paid': Amount.zero(),
        'payments': []
    }

    for txn in transactions:

        txn_dict = {
            'id': txn.id,
            'type': txn.transaction_type,
            'date': txn.transacted_on,
            'payment': Amount.zero(),
            'discount': Amount.zero(),
            'total': Amount.zero(),
            'jobs': {}
        }

        for entry in txn.entries.all():

            # we only work with receivable accounts from here on out
            if not entry.account.is_receivable:
                continue

            if entry.job not in jobs:
                # skip jobs we're not interested in
                continue

            job_dict = txn_dict['jobs'].setdefault(entry.job.id, {
                'job.id': entry.job.id,
                'code': entry.job.code,
                'name': entry.job.name,
                'payment': Amount.zero(),
                'discount': Amount.zero(),
                'total': Amount.zero()
            })

            if entry.entry_type == entry.PAYMENT:
                txn_dict['payment'] += entry.amount
                job_dict['payment'] += entry.amount

            elif entry.entry_type == entry.DISCOUNT:
                txn_dict['discount'] += entry.amount
                job_dict['discount'] += entry.amount

            if entry.entry_type in (entry.PAYMENT, entry.DISCOUNT):
                txn_dict['total'] += entry.amount
                job_dict['total'] += entry.amount

            if entry.entry_type in entry.TYPES_FOR_INVOICED_SUM:
                report['invoiced'] += entry.amount

            if entry.entry_type in entry.PAYMENT_TYPES+(entry.ADJUSTMENT,):
                report['paid'] += entry.amount

        if txn.transaction_type == txn.PAYMENT:
            report['payments'].append(txn_dict)

    return report


def create_adjustment_report(txn):

    adjustment = {
        'txn': txn
    }

    jobs = {}

    for entry in txn.entries.all():

        if not entry.account.is_receivable:
            continue

        job = jobs.setdefault(entry.job.id, {
            'job.id': entry.job.id,
            'code': entry.job.code,
            'name': entry.job.name,
            'amount': Amount.zero()
        })

        job['amount'] += entry.amount

    return adjustment


def create_refund_report(txn):

    refund = {
        'txn': txn
    }

    jobs = {}

    for entry in txn.entries.all():

        if not entry.account.is_receivable:
            continue

        job = jobs.setdefault(entry.job.id, {
            'job.id': entry.job.id,
            'code': entry.job.code,
            'name': entry.job.name,
            'amount': Amount.zero()
        })

        job['amount'] += entry.amount

    return refund


def generate_transaction_table(data, cols=('net', 'tax', 'gross')):
    t = []
    t += [('',)+cols+(None,)]
    t += [('progress',)+tuple(getattr(data['invoiced'], col) for col in cols)+(None,)]

    for txn in data['transactions']:
        if txn['type'] == Transaction.INVOICE:
            # only show invoice if it's not fully paid
            if txn['paid'].gross < txn['amount'].gross:
                amount = (txn['amount'] - txn['paid']).negate
                t += [(txn['type'],)+tuple(getattr(amount, col) for col in cols)+(txn,)]
        elif txn['type'] == Transaction.PAYMENT and\
                (txn['payment'].gross != 0 or txn['discount'].gross != 0):
            t += [(txn['type'],)+tuple(getattr(txn['payment'], col) for col in cols)+(txn,)]
            if txn['discount'].gross != 0:
                t += [('discount',)+tuple(getattr(txn['discount'], col) for col in cols)+(txn,)]

    return t

