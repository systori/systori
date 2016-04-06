# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from decimal import Decimal
from datetime import date
from django.utils.translation import ugettext as _


def split_gross_entries(apps, schema_editor):
    from systori.apps.company.models import Company
    from systori.apps.task.models import Job
    from systori.apps.accounting.models import Account, Entry
    from systori.apps.accounting.constants import TAX_RATE, SKR03_PARTIAL_PAYMENTS_CODE, SKR03_INCOME_CODE
    from systori.apps.accounting.constants import SKR03_CASH_DISCOUNT_CODE, SKR03_TAX_PAYMENTS_CODE
    from systori.apps.accounting.constants import SKR03_PROMISED_PAYMENTS_CODE
    from systori.lib.accounting.tools import extract_net_tax

    for company in Company.objects.all():
        company.activate()

        for job in Job.objects.all():
            for entry in job.account.entries.all():
                net, tax = extract_net_tax(entry.value, TAX_RATE)
                entry.value = net
                entry.value_type = entry.NET
                entry.save()
                entry.id = None
                entry.value = tax
                entry.value_type = entry.TAX
                entry.save()

        values_types = (
            (Entry.NET, (
                SKR03_PARTIAL_PAYMENTS_CODE,
                SKR03_INCOME_CODE,
                SKR03_CASH_DISCOUNT_CODE
            )),
            (Entry.TAX, (
                SKR03_TAX_PAYMENTS_CODE,
            )),
            (Entry.GROSS, (
                SKR03_PROMISED_PAYMENTS_CODE,
            ))
        )
        for value_type, account_codes in values_types:
            for account in Account.objects.filter(code__in=account_codes):
                for entry in account.entries.all():
                    if value_type == Entry.GROSS:
                        net, tax = extract_net_tax(entry.value, TAX_RATE)
                        entry.value = net
                        entry.value_type = entry.NET
                        entry.save()
                        entry.id = None
                        entry.value = tax
                        entry.value_type = entry.TAX
                        entry.save()
                    else:
                        entry.value_type = value_type
                        entry.save()


def migrate_proposals(apps, schema_editor):
    from systori.apps.company.models import Company
    from systori.apps.task.models import Job
    from systori.apps.document.models import Proposal
    from systori.apps.accounting.constants import TAX_RATE
    from systori.lib.accounting.tools import Amount

    for company in Company.objects.all():
        company.activate()

        for proposal in Proposal.objects.all():

            try:
                if 'total_base' not in proposal.json and 'jobs' not in proposal.json:
                    proposal.json['date'] = proposal.document_date
                    proposal.json['estimate_total'] = Amount(proposal.json['total_net'], proposal.json['total_gross']-proposal.json['total_net'])
                    proposal.json['jobs'] = []

                else:
                    proposal.json['estimate_total'] = Amount(proposal.json['total_base'], proposal.json['total_tax'])
                    del proposal.json['total_base'], proposal.json['total_tax'], proposal.json['total_gross']

                proposal.json['id'] = proposal.id
                proposal.json['title'] = _('Proposal')

                for job in proposal.json['jobs']:

                    if 'id' in job:
                        job['job.id'] = job['id']
                        del job['id']

                    else:
                        job_obj = Job.objects.filter(project=proposal.project, name=job['name']).get()
                        job['job.id'] = job_obj.id

                    job_estimate_net = Decimal('0.00')
                    for group in job['taskgroups']:
                        group['estimate_net'] = group['total']
                        del group['total']
                        job_estimate_net += Decimal(group['estimate_net'])
                        for task in group['tasks']:
                            task['estimate_net'] = task['total']
                            del task['total']
                    job['estimate'] = Amount.from_net(job_estimate_net, TAX_RATE)

                proposal.save()

            except:

                if proposal.status == proposal.DECLINED:
                    proposal.delete()
                else:
                    raise


def migrate_invoices(apps, schema_editor):
    from systori.apps.company.models import Company
    from systori.apps.document.models import Invoice
    from systori.apps.task.models import Job
    from systori.apps.accounting.report import create_invoice_report
    from systori.apps.accounting.constants import TAX_RATE
    from systori.lib.accounting.tools import Amount

    for company in Company.objects.all():
        company.activate()

        for invoice in Invoice.objects.all():

            invoice.json['debit'] = Amount(invoice.json['debit_net'], invoice.json['debit_tax'])

            if 'debits' not in invoice.json:
                invoice.json['jobs'] = []
                invoice.save()
                continue

            invoice.json['jobs'] = invoice.json['debits']
            del invoice.json['debits']

            jobs = Job.objects.filter(id__in=[job['job.id'] for job in invoice.json['jobs']])
            tdate = date(*map(int, invoice.json['transactions'][-1]['date'].split('-')))
            new_json = create_invoice_report(invoice.transaction, jobs, tdate)
            if (company.schema == 'mehr_handwerk' and invoice.id not in [86, 111]) or \
               (company.schema == 'montageservice_grad' and invoice.id not in [1]):
                assert new_json['debit'].gross == invoice.json['debit'].gross
                assert new_json['invoiced'].gross == invoice.json['debited_gross']
            invoice.json.update(new_json)

            for job in invoice.json['jobs']:

                taskgroup_total = Decimal('0.00')
                for taskgroup in job['taskgroups']:
                    taskgroup_total += taskgroup['total']
                job['progress'] = Amount.from_net(taskgroup_total, TAX_RATE)

                invoiced_total = Amount.zero()
                for debit in invoice.json['job_debits'].get(job['job.id'], []):
                    invoiced_total += debit['amount']
                job['invoiced'] = invoiced_total

                job['debit'] = Amount(job['amount_net'], job['amount_tax'])

                job['balance'] = Amount(job['balance_net'], job['balance_tax'])
                job['estimate'] = Amount.from_net(job['estimate_net'], TAX_RATE)

                job['is_itemized'] = job['invoiced'].gross == job['progress'].gross

            invoice.save()

def migrate_payments(apps, schema_editor):
    from systori.apps.company.models import Company
    from systori.apps.document.models import Payment, DocumentSettings
    from systori.apps.task.models import Job
    from systori.apps.accounting.models import Transaction
    from systori.lib.accounting.tools import Amount

    print('payment migration..')

    for company in Company.objects.all():
        company.activate()

        for t in Transaction.objects.filter(transaction_type=Transaction.PAYMENT):

            job = None
            job_dict = None

            jobs = {}
            split_t = Amount.zero()
            discount_t = Amount.zero()
            adjustment_t = Amount.zero()
            credit_t = Amount.zero()

            if t.id in [9, 154, 297, 307]:
                entry = t.entries.first()
                print('Company: ', company.schema, ', Transaction ID:', t.id, ', Date:', t.transacted_on, ', Bank:', entry.account.name, ', Amount:', entry.amount.gross, ', Entries: ', t.entries.count())
                continue

            bank_account = None
            for entry in t.entries.all():

                if entry.account.is_bank or entry.account.name == 'VR Bank Rhein-Neckar eG':
                    bank_account = entry.account
                    continue

                job = entry.job
                if job:
                    job_dict = jobs.setdefault(job.id, {
                        'job.id': job.id,
                        'name': job.name,
                        'split': Amount.zero(),
                        'discount': Amount.zero(),
                        'adjustment': Amount.zero(),
                        'credit': Amount.zero()
                    })

                    if entry.entry_type == entry.PAYMENT:
                        job_dict['split'] += entry.amount.negate
                        split_t += entry.amount

                    elif entry.entry_type == entry.DISCOUNT:
                        job_dict['discount'] += entry.amount.negate
                        discount_t += entry.amount

                    elif entry.entry_type == entry.ADJUSTMENT:
                        job_dict['adjustment'] += entry.amount.negate
                        adjustment_t += entry.amount

                    if entry.entry_type in (entry.PAYMENT, entry.DISCOUNT, entry.ADJUSTMENT):
                        job_dict['credit'] += entry.amount.negate
                        credit_t += entry.amount

            assert job
            assert bank_account

            letterhead = DocumentSettings.get_for_language('de').invoice_letterhead
            payment = Payment(
                project=job.project,
                document_date=t.transacted_on,
                transaction=t,
                letterhead=letterhead
            )
            payment.json.update({
                'bank_account': bank_account.id,
                'date': t.transacted_on,
                'payment': credit_t.negate.gross,
                'discount': Decimal('0.00'),
                'split_total': split_t.negate,
                'discount_total': discount_t.negate,
                'adjustment_total': adjustment_t.negate,
                'credit_total': credit_t.negate,
                'jobs': jobs.values(),
            })
            payment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20160221_0254'),
        ('document', '0003_new_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='value_type',
            field=models.CharField(max_length=32, default='gross', choices=[('net', 'Net'), ('tax', 'Tax'), ('gross', 'Gross')], verbose_name='Value Type'),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name='entry',
            old_name='amount',
            new_name='value'
        ),
        migrations.AlterField(
            model_name='entry',
            name='value',
            field=models.DecimalField(verbose_name='Value', decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name='entry',
            name='entry_type',
            field=models.CharField(max_length=32, default='other', choices=[('payment', 'Payment'), ('refund-credit', 'Refund Credit'), ('discount', 'Discount'), ('work-debit', 'Work Debit'), ('flat-debit', 'Flat Debit'), ('refund', 'Refund'), ('adjustment', 'Adjustment'), ('other', 'Other')], verbose_name='Entry Type'),
        ),
        migrations.RemoveField(
            model_name='entry',
            name='tax_rate',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(max_length=32, verbose_name='Transaction Type', null=True, choices=[('invoice', 'Invoice'), ('payment', 'Payment'), ('adjustment', 'Adjustment'), ('refund', 'Refund')]),
        ),
        migrations.RunPython(split_gross_entries),
        migrations.RunPython(migrate_proposals),
        migrations.RunPython(migrate_invoices),
        migrations.RunPython(migrate_payments)
    ]
