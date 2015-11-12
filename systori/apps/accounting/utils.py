from decimal import Decimal
from .models import Transaction
from ..task.models import Job
from .constants import TAX_RATE


def get_transactions_for_jobs(jobs, transacted_on_or_before=None):

    txns = Transaction.objects\
        .filter(entries__account__job__in=jobs)\
        .distinct()\
        .order_by('transacted_on')

    if transacted_on_or_before:
        txns = txns.filter(transacted_on__lte=transacted_on_or_before)

    result = []
    for tx in txns:

        tx_dict = {
            'id': tx.id,
            'type': tx.transaction_type,
            'date': tx.transacted_on,
            'transaction_total': Decimal(0.0),
            'jobs_total': Decimal(0.0),
            'jobs': {}
        }

        if tx.transaction_type == tx.INVOICE:
            invoice = tx.invoice
            tx_dict.update({
                'invoice.id': invoice.id,
                'transaction_total': invoice.json['debit_gross'],
            })

        for entry in tx.entries.prefetch_related('account__job__project').all():

            if tx.transaction_type == tx.PAYMENT and entry.account.is_bank:
                assert tx_dict['transaction_total'] == Decimal(0.0)
                tx_dict['transaction_total'] = entry.amount * -1  # bank deposit entry

            try:

                job = entry.account.job  # this is the part that can throw exception

                if job not in jobs:
                    continue

                if job.id not in tx_dict['jobs']:
                    tx_dict['jobs'][job.id] = {
                        'job.id': job.id,
                        'code': job.code,
                        'name': job.name,
                        'amount': Decimal(0.0),
                        'amount_net': Decimal(0.0),
                        'amount_tax': Decimal(0.0),
                        'discount': Decimal(0.0),
                        'entries': []
                    }

                job_dict = tx_dict['jobs'][job.id]

                if entry.entry_type in (entry.PAYMENT,):
                    job_dict['amount'] += entry.amount

                elif entry.entry_type in (entry.WORK_DEBIT, entry.FLAT_DEBIT):
                    job_dict['amount'] += entry.amount

                elif entry.entry_type == entry.DISCOUNT:
                    job_dict['discount'] += entry.amount
                    continue

                else:
                    raise NotImplemented("Don't know how to handle '{}'.".format(entry.entry_type))

                job_dict['amount_net'] = round(job_dict['amount'] / (1+TAX_RATE), 2)
                job_dict['amount_tax'] = job_dict['amount'] - job_dict['amount_tax']

                tx_dict['jobs_total'] += job_dict['amount']

            except Job.DoesNotExist:
                pass

        result.append(tx_dict)

    return result
