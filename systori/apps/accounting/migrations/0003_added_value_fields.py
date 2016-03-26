# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from decimal import Decimal


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


def recalculate_invoices(apps, schema_editor):
    from systori.apps.company.models import Company
    from systori.apps.document.models import Invoice, Payment, DocumentSettings
    from systori.apps.task.models import Job
    from systori.apps.accounting.models import Transaction
    from systori.apps.accounting.report import create_invoice_report
    from systori.apps.accounting.constants import TAX_RATE
    from systori.lib.accounting.tools import Amount

    for company in Company.objects.all():
        company.activate()

        for invoice in Invoice.objects.all():
            if 'debits' not in invoice.json:
                print('skipping invoice #{}'.format(invoice.id))
                continue
            invoice.json['jobs'] = invoice.json['debits']
            del invoice.json['debits']

            invoice.json['debit'] = Amount(invoice.json['debit_net'], invoice.json['debit_tax'])
            del invoice.json['debit_net'], invoice.json['debit_tax']
            job_ids = []
            for job in invoice.json['jobs']:
                job_ids.append(job['job.id'])
                job['debit'] = Amount(job['amount_net'], job['amount_tax'])
                del job['amount_net'], job['amount_tax']
                job['invoiced'] = Amount(job['debited_net'], job['debited_tax'])
                del job['debited_net'], job['debited_tax']
                job['balance'] = Amount(job['balance_net'], job['balance_tax'])
                del job['balance_net'], job['balance_tax']
                job['estimate'] = Amount.from_net(job['estimate_net'], TAX_RATE)
                del job['estimate_net']
                job['progress'] = Amount.from_net(job['itemized_net'], TAX_RATE)
                del job['itemized_net']
            jobs = Job.objects.filter(id__in=job_ids)
            new_json = create_invoice_report(invoice.transaction, jobs, invoice.document_date)
            print(invoice.id)
            if invoice.id == 85:
                pass
            # TODO: Fix failing asserts.
            #assert len(new_json['transactions']) == len(invoice.json['transactions'])
            print(new_json['invoiced'].gross, invoice.json['debited_gross'])
            #assert new_json['invoiced'].gross == invoice.json['debited_gross']
            invoice.json.update(new_json)
            invoice.save()

        for t in Transaction.objects.filter(transaction_type=Transaction.PAYMENT):

            job = None

            jobs = {}
            split_t = Amount.zero()
            discount_t = Amount.zero()
            adjustment_t = Amount.zero()
            credit_t = Amount.zero()

            bank_account = None
            for entry in t.entries.all():

                if entry.account.is_bank:
                    bank_account = entry.account

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

            if bank_account and job:
                letterhead = DocumentSettings.get_for_language('de').invoice_letterhead
                payment = Payment(
                    project=job.project,
                    document_date=t.transacted_on,
                    transaction=t,
                    letterhead=letterhead
                )
                payment.json.update({
                    'bank.id': bank_account.id,
                    'date': t.transacted_on,
                    'payment': credit_t.negate.gross,
                    'discount': Decimal('0.00'),
                    'split_total': credit_t.negate,
                    'discount_total': discount_t.negate,
                    'adjustment_total': adjustment_t.negate,
                    'credit_total': credit_t.negate,
                    'jobs': jobs.values(),
                })
                payment.save()
            else:
                if job:
                    print('No Bank Account: %s' % (job.project.name,))
                else:
                    print('No Job')


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
        migrations.RunPython(recalculate_invoices)
    ]
