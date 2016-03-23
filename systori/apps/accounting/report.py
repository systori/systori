from django.core.exceptions import ObjectDoesNotExist
from .models import Transaction
from systori.lib.accounting.tools import Amount


def _transaction_sort_key(txn):
    """
    If there are payments and invoices created on the same day
    we want to make sure to process the payments first and then
    the invoices. Otherwise the transaction history on an
    invoice will look like a drunk cow licked it, that's bad.
    :param txn:
    :return: sort key
    """
    txn_date = txn.transacted_on.isoformat()[:10]
    type_weight = '0' if txn.transaction_type == txn.PAYMENT else '1'
    txn_id = str(txn.id)  # sort multiple invoices on same day by primary key id
    return txn_date+type_weight+txn_id


def create_invoice_report(invoice_txn, jobs, transacted_on_or_before=None):
    """
    :param invoice_txn: transaction that should be excluded from 'open claims' (unpaid amount)
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
        'payments': [],
        'unpaid': Amount.zero(),
        'debit': Amount.zero()
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
                if txn.id == invoice_txn.id:
                    report['debit'] += entry.amount

            if entry.entry_type in entry.TYPES_FOR_PAID_SUM:
                report['paid'] += entry.amount

        if txn.transaction_type == txn.PAYMENT:
            report['payments'].append(txn_dict)

    report['unpaid'] = (report['invoiced'] + report['paid'] - report['debit']).negate

    return report


def create_invoice_table(report, cols=('net', 'tax', 'gross')):
    t = []
    t += [('',)+cols+(None,)]
    t += [('progress',)+tuple(getattr(report['invoiced'], col) for col in cols)+(None,)]

    for txn in report['payments']:
        t += [(txn['type'],)+tuple(getattr(txn['payment'], col) for col in cols)+(txn,)]
        if txn['discount'].gross != 0:
            t += [('discount',)+tuple(getattr(txn['discount'], col) for col in cols)+(txn,)]

    if report['unpaid'].gross != 0:
        t += [('unpaid',)+tuple(getattr(report['unpaid'], col) for col in cols)+(None,)]

    t += [('debit',)+tuple(getattr(report['debit'], col) for col in cols)+(None,)]

    return t


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


def create_adjustment_table(report):
    return []


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
