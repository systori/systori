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
    Proposal = apps.get_model('document', 'Proposal')

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

        for proposal in Proposal.objects.all():

            if 'total_gross' not in proposal.json or \
                    (proposal.json['total_gross'] == 0 and proposal.amount > 0):
                proposal.json['total_gross'] = proposal.amount
                proposal.json['total_net'], job['total_tax'] = extract_net_tax(D(proposal.amount), D('0.19'))
                proposal.save()
