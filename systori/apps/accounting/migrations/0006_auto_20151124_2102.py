# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from decimal import Decimal as D
from systori.apps.accounting.report import prepare_transaction_report
from systori.lib.accounting.tools import extract_net_tax


def is_bank(account):
    if account.code.isdigit():
        code = int(account.code)
        if 1200 <= code <= 1288:
            return True
    return False


def set_missing_values(apps, schema_editor):
    from systori.apps.task.models import Job
    from systori.apps.company.models import Company
    Account = apps.get_model('accounting', 'Account')
    Entry = apps.get_model('accounting', 'Entry')
    Invoice = apps.get_model('document', 'Invoice')

    for company in Company.objects.all():
        company.activate()

        for asset in Account.objects.filter(account_type='asset'):
            asset.asset_type = 'bank' if is_bank(asset) else 'receivable'
            asset.save()

        for entry in Entry.objects.all():
            if entry.entry_type != "other":
                if entry.entry_type == "final-debit":
                    entry.entry_type = "work-debit"
                entry.tax_rate = D('0.19')
                entry.save()

        invoice_idx = 0
        for invoice in Invoice.objects.all():
            if 'debits' not in invoice.json:
                continue

            if invoice.id == 62:
                pass

            # TODO: write some unit tests to make sure that invoices created/updated set the correct document_date

            if invoice.id in [73, 76, 77, 78]:
                invoice.transaction.transacted_on = invoice.document_date
                invoice.transaction.save()

            #print(invoice.project_id, invoice.id)
            assert invoice.transaction.transacted_on == invoice.document_date

            jobs = Job.objects.filter(id__in=[d['job.id'] for d in invoice.json['debits']])
            report = prepare_transaction_report(jobs, invoice.document_date)

            # make sure none of the totals or balances changed since that would be bad...
            # project-99 and project-51 need to have invoice recreated to match previously generated invoice
            # project-106, invoice 62 was off by 6 euros....
            # project-106, invoice 67 was off by 7 euros....
            # project-106, invoice 70 was off by 1653 euros....
            if invoice.id not in [29, 31, 37, 39, 40, 44, 46, 54, 55, 60, 62, 63, 67, 70, 71] and company.name != 'Demo':  # these are off by one cent...
                for field in ['debited_gross', 'debited_net', 'debited_tax']:
                    #print(invoice.project_id, invoice.id, D(report[field]), round(D(invoice.json[field]), 2), invoice.json[field])
                    assert D(report[field]) == round(D(invoice.json[field]), 2)
            elif company.name != 'Demo':
                invoice_idx += 1
                for field in ['debited_gross', 'debited_net', 'debited_tax']:
                    old = round(D(invoice.json[field]), 2)
                    new = D(report[field])
                    diff = new-old
                    if diff != 0:
                        print('{} | [{p}](https://systori.com/project-{pid}) | [{i}](https://systori.com/project-{pid}/invoice-print-{iid}.pdf) | {} | {} | {} | {}'.format(
                                invoice_idx, field, old, new, diff,
                                p=invoice.project.name, pid=invoice.project_id,
                                i=invoice.json['title'], iid=invoice.id))

            if company.name != 'Demo':
                #print(invoice.project_id, invoice.id, D(report['transactions'][-1]['gross']), round(D(invoice.json['debit_gross']), 2))
                assert D(report['transactions'][-1]['gross']) == round(D(invoice.json['debit_gross']), 2)

            for job in invoice.json['debits']:
                job['amount_net'] = job['debit_net']
                job['amount_gross'] = job['debit_amount']
                job['amount_tax'] = job['debit_tax']
                job['is_override'] = job['is_flat']
                job['override_comment'] = job['debit_comment']
                job['debited_gross'] = job['debited']
                job['debited_net'], job['debited_tax'] = extract_net_tax(D(job['debited']), D('0.19'))
                job['balance_gross'] = job['balance']
                job['balance_net'], job['balance_tax'] = extract_net_tax(D(job['balance']), D('0.19'))
                job['estimate_net'] = extract_net_tax(D(job['estimate']), D('0.19'))[0]
                job['itemized_net'] = extract_net_tax(D(job['itemized']), D('0.19'))[0]

            invoice.json.update(report)

            invoice.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_entry_job'),
        ('document', '0006_auto_20151119_2148'),
        ('task', '0007_job_is_revenue_recognized'),
        ('project', '0005_remove_project_account')
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='tax_rate',
            field=models.DecimalField(decimal_places=2, max_digits=14, default=0, verbose_name='Tax Rate'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=14, verbose_name='Amount'),
        ),
        migrations.AddField(
            model_name='account',
            name='asset_type',
            field=models.CharField(max_length=32, choices=[('bank', 'Bank'), ('receivable', 'Accounts Receivable')], verbose_name='Asset Type', null=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='entry_type',
            field=models.CharField(verbose_name='Entry Type', choices=[('payment', 'Payment'), ('discount', 'Discount'), ('work-debit', 'Work Debit'), ('flat-debit', 'Flat Debit'), ('adjustment', 'Adjustment'), ('other', 'Other')], default='other', max_length=32),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(max_length=32, choices=[('invoice', 'Invoice'), ('final-invoice', 'Final Invoice'), ('payment', 'Payment'), ('adjustment', 'Adjustment')], verbose_name='Transaction Type', null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_revenue_recognized',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_missing_values),
    ]
