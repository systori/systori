from decimal import Decimal as D
from django.core.exceptions import ObjectDoesNotExist
from .models import Transaction
from systori.lib.accounting.tools import extract_net_tax
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


def prepare_transaction_report(jobs, transacted_on_or_before=None):
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

    report = {
        # progress
        'debited_net': D('0.00'),
        'debited_tax': D('0.00'),
        'debited_gross': D('0.00'),
        # payments and invoices
        'transactions': [],
    }

    # aggregates all payments per job, used by auto-pay algorithm later
    payments = {
        job.id: {
            'net': D('0.00'),
            'tax': D('0.00'),
            'gross': D('0.00')
        } for job in jobs
    }

    for txn in transactions:

        txn_dict = {
            'id': txn.id,
            'type': txn.transaction_type,
            'date': txn.transacted_on,

            'net': D('0.00'),
            'tax': D('0.00'),
            'gross': D('0.00'),

            'jobs': {}
        }

        if txn.transaction_type == txn.INVOICE:
            txn_dict.update({
                'paid_net': D('0.00'),
                'paid_tax': D('0.00'),
                'paid_gross': D('0.00'),
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
                'is_reconciled': False,

                'payment_received': D('0.00'),  # actual amount received from customer

                'payment_applied_net': D('0.00'),
                'payment_applied_tax': D('0.00'),
                'payment_applied_gross': D('0.00'),  # part of payment applied to this set of 'jobs'

                'discount_applied_net': D('0.00'),
                'discount_applied_tax': D('0.00'),
                'discount_applied_gross': D('0.00'),  # discount applied to this set of 'jobs'

                'adjustment_applied_net': D('0.00'),
                'adjustment_applied_tax': D('0.00'),
                'adjustment_applied_gross': D('0.00'),
            })

        for entry in txn.entries.prefetch_related('job', 'account__job__project').all():

            # extract payment entry info
            if txn.transaction_type == txn.PAYMENT and entry.account.is_bank:
                txn_dict['is_reconciled'] = entry.is_reconciled
                txn_dict['payment_received'] = entry.amount * -1
                continue

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
                    'net': D('0.00'),
                    'tax': D('0.00'),
                    'gross': D('0.00'),
                }
                if txn.transaction_type == txn.PAYMENT:
                    txn_dict['jobs'][job.id].update({
                        'payment_applied_net': D('0.00'),
                        'payment_applied_tax': D('0.00'),
                        'payment_applied_gross': D('0.00'),

                        'discount_applied_net': D('0.00'),
                        'discount_applied_tax': D('0.00'),
                        'discount_applied_gross': D('0.00'),

                        'adjustment_applied_net': D('0.00'),
                        'adjustment_applied_tax': D('0.00'),
                        'adjustment_applied_gross': D('0.00'),
                    })

            entry_gross = entry.amount
            entry_net, entry_tax = extract_net_tax(entry_gross, TAX_RATE)

            job_dict = txn_dict['jobs'][job.id]

            txn_dict['net'] += entry_net
            txn_dict['tax'] += entry_tax
            txn_dict['gross'] += entry_gross
            job_dict['net'] += entry_net
            job_dict['tax'] += entry_tax
            job_dict['gross'] += entry_gross

            if entry.entry_type == entry.ADJUSTMENT:
                # adjustments reduce the total debited
                report['debited_net'] += entry_net
                report['debited_tax'] += entry_tax
                report['debited_gross'] += entry_gross

                txn_dict['adjustment_applied_net'] += entry_net
                txn_dict['adjustment_applied_tax'] += entry_tax
                txn_dict['adjustment_applied_gross'] += entry_gross
                job_dict['adjustment_applied_net'] += entry_net
                job_dict['adjustment_applied_tax'] += entry_tax
                job_dict['adjustment_applied_gross'] += entry_gross

            elif entry.entry_type == entry.PAYMENT:
                txn_dict['payment_applied_net'] += entry_net
                txn_dict['payment_applied_tax'] += entry_tax
                txn_dict['payment_applied_gross'] += entry_gross
                job_dict['payment_applied_net'] += entry_net
                job_dict['payment_applied_tax'] += entry_tax
                job_dict['payment_applied_gross'] += entry_gross

            elif entry.entry_type == entry.DISCOUNT:
                txn_dict['discount_applied_net'] += entry_net
                txn_dict['discount_applied_tax'] += entry_tax
                txn_dict['discount_applied_gross'] += entry_gross
                job_dict['discount_applied_net'] += entry_net
                job_dict['discount_applied_tax'] += entry_tax
                job_dict['discount_applied_gross'] += entry_gross

        for job in txn_dict['jobs'].values():
            if txn.transaction_type == txn.PAYMENT:
                jid = job['job.id']
                payments[jid]['net'] += job['net']
                payments[jid]['tax'] += job['tax']
                payments[jid]['gross'] += job['gross']

        report['transactions'].append(txn_dict)
        if txn.transaction_type != txn.PAYMENT:
            report['debited_net'] += txn_dict['net']
            report['debited_tax'] += txn_dict['tax']
            report['debited_gross'] += txn_dict['gross']

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

            if payment['gross'] == 0:
                job['paid_net'] = D('0.00')
                job['paid_tax'] = D('0.00')
                job['paid_gross'] = D('0.00')
                continue  # payments used up

            elif job['gross'] >= -payment['gross']:
                # payments left is less than the invoiced amount...
                # pay invoice with all that's left
                job['paid_gross'] = -payment['gross']
                job['paid_net'] = -payment['net']
                job['paid_tax'] = -payment['tax']

            else:
                # still have enough payments left to cover the entire invoice...
                # pay the invoice in full
                job['paid_gross'] = job['gross']
                job['paid_net'] = job['net']
                job['paid_tax'] = job['tax']

            # reduce payment total by how much was applied to this invoice
            payment['gross'] += job['paid_gross']
            payment['net'] += job['paid_net']
            payment['tax'] += job['paid_tax']

            invoice['paid_net'] += job['paid_net']
            invoice['paid_tax'] += job['paid_tax']
            invoice['paid_gross'] += job['paid_gross']

    return report


def generate_transaction_table(data, cols=('net', 'tax', 'gross')):
    t = []
    t += [('',)+cols+(None,)]
    t += [('progress',)+tuple(data['debited_'+col] for col in cols)+(None,)]

    for txn in data['transactions']:
        if txn['type'] == Transaction.INVOICE:
            # only show invoice if it's not fully paid
            if txn['paid_gross'] < txn['gross']:
                vals = {
                    'gross': txn['gross'] - txn['paid_gross'],
                    'net': txn['net'] - txn['paid_net'],
                    'tax': txn['tax'] - txn['paid_tax']
                }
                t += [(txn['type'],)+tuple(-vals[col] for col in cols)+(txn,)]
        else:
            t += [(txn['type'],)+tuple(txn['payment_applied_'+col] for col in cols)+(txn,)]
            if txn['discount_applied_gross'] != 0:
                t += [('discount',)+tuple(txn['discount_applied_'+col] for col in cols)+(txn,)]

    return t

