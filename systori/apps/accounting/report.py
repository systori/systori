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


def prepare_transaction_report(jobs, transacted_on_or_before=None):
    """
    :param jobs: limit transaction details to specific set of jobs
    :param transacted_on_or_before: limit transactions up to and including a certain date
    :return: serializable data structure
    """

    txns_query = Transaction.objects \
        .filter(entries__job__in=jobs) \
        .prefetch_related('invoice') \
        .prefetch_related('entries__job__project') \
        .prefetch_related('entries__account') \
        .distinct()

    if transacted_on_or_before:
        txns_query = txns_query.filter(transacted_on__lte=transacted_on_or_before)

    transactions = list(txns_query)
    transactions.sort(key=_transaction_sort_key)

    report = {
        'invoiced': Amount.zero(),
        'transactions': [],
    }

    # aggregates all payments per job, used by auto-pay algorithm later
    payments = {job.id: Amount.zero() for job in jobs}

    for txn in transactions:

        txn_dict = {
            'id': txn.id,
            'type': txn.transaction_type,
            'date': txn.transacted_on,
            'amount': Amount.zero(),
            'jobs': {}
        }

        if txn.transaction_type == txn.INVOICE:
            txn_dict.update({
                'paid': Amount.zero()
            })
            try:
                txn_dict.update({
                    'invoice_id': txn.invoice.id,
                    'invoice_status': txn.invoice.status,
                    'invoice_title': txn.invoice.json['title']
                })
            except ObjectDoesNotExist:
                pass

        elif txn.transaction_type == txn.PAYMENT:
            txn_dict.update({
                'payment': Amount.zero(),   # part of payment applied to this set of 'jobs'
                'discount': Amount.zero(),  # discount applied to this set of 'jobs'
            })
        else:
            raise NotImplementedError('Unsupported transaction type: %s' % (txn.transaction_type,))

        for entry in txn.entries.all():

            # we only work with receivable accounts from here on out
            if not entry.account.is_receivable:
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
                    'amount': Amount.zero()
                }
                if txn.transaction_type in (txn.PAYMENT, txn.ADJUSTMENT):
                    txn_dict['jobs'][job.id].update({
                        'payment': Amount.zero(),  # actual amount received from customer
                        'discount': Amount.zero()  # discount applied to this set of 'jobs'
                    })

            job_dict = txn_dict['jobs'][job.id]

            txn_dict['amount'] += entry.amount
            job_dict['amount'] += entry.amount

            if entry.entry_type == entry.PAYMENT:
                txn_dict['payment'] += entry.amount
                job_dict['payment'] += entry.amount

            elif entry.entry_type == entry.DISCOUNT:
                txn_dict['discount'] += entry.amount
                job_dict['discount'] += entry.amount

            if entry.entry_type in entry.PAYMENT_TYPES+(entry.ADJUSTMENT,):
                payments[job.id] += entry.amount

            if entry.entry_type in entry.TYPES_FOR_INVOICED_SUM:
                report['invoiced'] += entry.amount

        report['transactions'].append(txn_dict)

    # Automated Payment Algorithm
    # We start with a total of all payments the customer has made to a
    # particular job. Then we loop over all of the invoices from first to last
    # applying as much of the payment as we can to the invoices until there
    # is no payment left.
    for invoice in report['transactions']:

        if invoice['type'] != txn.INVOICE:
            continue

        for job in invoice['jobs'].values():
            payment = payments[job['job.id']]

            if payment.gross == 0:
                job['paid'] = Amount.zero()
                continue  # payments used up

            elif job['amount'].gross >= payment.negate.gross:
                # payments left is less than the invoiced amount...
                # pay invoice with all that's left
                job['paid'] = payment.negate

            else:
                # still have enough payments left to cover the entire invoice...
                # pay the invoice in full
                job['paid'] = job['amount']

            # reduce payment total by how much was applied to this invoice
            payments[job['job.id']] += job['paid']

            invoice['paid'] += job['paid']

    return report


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

