from decimal import Decimal
from .models import Transaction
from ..task.models import Job

def get_transactions_for_jobs(jobs):

    txns = Transaction.objects\
        .filter(entries__account__job__in=jobs)\
        .distinct()\
        .order_by('received_on')

    result = []
    for tx in txns:

        tx_dict = {
            'id': tx.id,
            'type': tx.transaction_type,
            'date': tx.received_on,
            'transaction_total': Decimal(0.0),
            'jobs_total': Decimal(0.0),
            'jobs': {}
        }

        if tx.transaction_type == tx.INVOICE:
            invoice = tx.invoice
            tx_dict.update({
                'date': tx.recorded_on,
                'invoice.id': invoice.id,
                'transaction_total': invoice.json['debit_gross'],
            })

        for entry in tx.entries.prefetch_related('account__job__project').all():

            if tx.transaction_type == tx.PAYMENT and entry.account.is_bank:
                tx_dict['transaction_total'] += entry.amount * -1  # bank deposit entry

            try:

                job = entry.account.job

                if job not in jobs:
                    continue

                if job.id not in tx_dict['jobs']:
                    tx_dict['jobs'][job.id] = {
                        'job.id': job.id,
                        'code': job.code,
                        'name': job.name,
                        'amount': Decimal(0.0),
                        'entries': []
                    }

                tx_dict['jobs'][job.id]['amount'] += entry.amount
                tx_dict['jobs'][job.id]['entries'].append(
                    {'type': entry.entry_type, 'amount': entry.amount}
                )

            except Job.DoesNotExist:
                pass

        for job in tx_dict['jobs'].values():
            tx_dict['jobs_total'] += job['amount']

        result.append(tx_dict)

    #payments = []
    #for job in jobs:
    #    for credit in job.account.payments():
    #        tr = credit.transaction
    #        if (tr.id, tr) not in payments:
    #            payments.append((tr.id, tr))

    #payments.sort(key=lambda i: i[0])
    #return [p[1] for p in payments]

    # Flatten and sort list of debits + invoices + payments
    #debits = []
    #invoices = [('invoice', i.document_date, i, None) for i in project.invoices.all()]
    #payments = []
    #for job in project.jobs.all():
        #debits.extend([('debit', d.transaction.recorded_on.date(), d, job) for d in job.account.debits().all()])
        #payments.extend([('payment', p.received_on, p, job) for p in job.account.payments().all()])
    #all_the_things = []#invoices + payments
    #all_the_things.sort(key=lambda i: i[1])

    # Now we add the discounts
    #transactions = []
    #for r_type, r_date, payment, job in all_the_things:
    #    transactions.append((r_type, r_date, payment, job))
    #    if r_type != 'payment': continue
    #    for discount in payment.transaction.discounts_to_account(job.account).all():
    #        transactions.append(('discount', r_date, discount, job))

    #return transactions
    return result


def get_job_payments(job):
    return []
