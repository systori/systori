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

            #if entry.id in [865, 866]:  # increases discount applied to job account, both entries
            #    entry.amount -= D('0.01')
            #    entry.save()

        invoice_idx = 0
        for invoice in Invoice.objects.all():
            if 'debits' not in invoice.json:
                continue

            if invoice.id == 54:
                pass

            # TODO: write some unit tests to make sure that invoices created/updated set the correct document_date

            if invoice.id in [73, 76, 77, 78]:
                invoice.transaction.transacted_on = invoice.document_date
                invoice.transaction.save()

            #print(invoice.project_id, invoice.id)
            assert invoice.transaction.transacted_on == invoice.document_date

            jobs = Job.objects.filter(id__in=[d['job.id'] for d in invoice.json['debits']])
            report = prepare_transaction_report(jobs, invoice.document_date)

            debited_net = D('0')
            for debit in invoice.json['debits']:
                for taskgroup in debit['taskgroups']:
                    debited_net += round(D(taskgroup['total']), 2)

            # these actually had the wrong net calculation, probably because invoices used to be entered with gross
            # 75, 76, 77 = flat invoice
            if invoice.id not in [44, 46, 63, 69, 74, 75, 76, 77, 78, 81] and company.name != 'Demo':
                #print(invoice.project_id, invoice.id, debited_net, round(D(invoice.json['debited_net']), 2))
                assert debited_net == round(D(invoice.json['debited_net']), 2)

            if company.name != 'Demo' and\
                    (abs(D(report['debited_net']) - round(D(invoice.json['debited_net']), 2)) > 0 or\
                     abs(D(report['debited_gross']) - round(D(invoice.json['debited_gross']), 2)) > 0):
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
            field=models.CharField(verbose_name='Transaction Type', choices=[('invoice', 'Invoice'), ('payment', 'Payment'), ('adjustment', 'Adjustment')], max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_revenue_recognized',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_missing_values),
    ]
