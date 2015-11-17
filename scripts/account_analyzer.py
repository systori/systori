from decimal import Decimal
from datetime import timedelta


SHOW_SKIPPED = False


def migrate_accounts(company):
    from systori.apps.project.models import Project
    from systori.apps.accounting.models import Account, Transaction, Entry, create_account_for_job
    from systori.apps.accounting.constants import TAX_RATE, SKR03_INCOME_CODE
    from systori.apps.accounting.utils import get_transactions_for_jobs
    from systori.apps.accounting import skr03
    from systori.apps.task.models import Job
    from systori.apps.document.models import Invoice

    from systori.lib.templatetags.customformatting import money

    for project in Project.objects.without_template():
        project.account.code = int(project.account.code) + 1000
        project.account.save()

    for job in Job.objects.all():
        if job.account:
            job.account.delete()

    for job in Job.objects.all():
        job.account = create_account_for_job(job)
        job.save()

    for project in Project.objects.without_template().order_by('id'):

        if not project.invoices.exists():
            if project.account.entries.exists():
                if SHOW_SKIPPED:
                    print("Project #{} - {}".format(project.id, project.name))
                    print('  !!! Has entries but no invoices. !!!')
                    print('')
            else:
                if SHOW_SKIPPED:
                    print("Project #{} - {}".format(project.id, project.name))
                    print('  !!! No invoices and no entries. !!!')
                    print('')
            continue


        no_json = False
        for invoice in project.invoices.all():
            if not invoice.json:
                no_json = True
                if SHOW_SKIPPED:
                    print("Project #{} - {}".format(project.id, project.name))
                    print('  !!! Old invoices, no json. !!!')
                    print('')
                break

        if no_json:
            continue

        print("\nProject #{} - {}".format(project.id, project.name))

        final_debits = []

        parent_invoice = None
        total_invoices = project.invoices.count()
        for i_invoice, invoice in enumerate(project.invoices.all()):

            if i_invoice < total_invoices-1:
                invoice.status = invoice.SENT
            else:
                invoice.status = invoice.DRAFT

            if not parent_invoice:
                parent_invoice = invoice
            else:
                invoice.parent = parent_invoice

            print("\n Invoice #{} - {} - {}".format(invoice.id, invoice.invoice_no, invoice.document_date.isoformat()))
            invoice_amount = Decimal(0.0)
            pre_tax_invoice = Decimal(0.0)

            if invoice.id == 47:
                pass

            match_criteria = [
                {'recorded_on__startswith': invoice.created_on.isoformat(' ')[:19]},
                {'recorded_on__startswith': invoice.created_on.isoformat(' ')[:18]},
                #{'recorded_on__gte': invoice.created_on-timedelta(minutes=2),
                # 'recorded_on__lte': invoice.created_on+timedelta(minutes=2)},
            ]
            print('  Finding corresponding transaction...')
            print('  >{}'.format(invoice.created_on.isoformat(' ')))
            old_transaction = None
            for criteria in match_criteria:
                for key, val in criteria.items():
                    print('  ?{} :{}'.format(val, key))
                matches = Transaction.objects.filter(entries__account=project.account).filter(**criteria).distinct()
                if matches.count() == 1:
                    old_transaction = matches.get()
                    print('  !{}'.format(old_transaction.recorded_on))
                    break
                elif matches.count() == 0:
                    print('  No matches.')
                elif matches.count() > 1:
                    print('  Multiple matches:')
                    for match in matches:
                        print('   {}'.format(match.recorded_on))

            invoice.json['is_final'] = False
            if old_transaction:
                for entry in old_transaction.entries.all():
                    if entry.account.code == SKR03_INCOME_CODE:
                        invoice.json['is_final'] = True
                        break

            invoice.json['debits'] = []
            debits = []
            for json_job in invoice.json.pop('jobs'):

                job = project.jobs.get(name=json_job['name'], job_code=int(json_job['code']))
                json_job['job.id'] = job.id
                json_job['is_invoiced'] = True
                json_job['flat_amount'] = 0.0
                json_job['is_flat'] = False

                pre_tax_amount = Decimal(0.0)
                for json_taskgroup in json_job['taskgroups']:
                    pre_tax_amount += Decimal(json_taskgroup['total'])

                amount = round(pre_tax_amount * Decimal(1.19), 2)
                already_debited = job.account.debits().total

                amount -= already_debited
                if amount < Decimal(0.0):
                    amount = Decimal(0.0)

                invoice_amount += amount
                pre_tax_invoice += round(amount / (1+TAX_RATE), 2)

                json_job['debit_amount'] = amount
                json_job['debit_comment'] = ""
                json_job['debited'] = already_debited
                json_job['balance'] = 0.0  # we don't have payments yet
                json_job['estimate'] = round(job.estimate_total * (1+TAX_RATE), 2)
                json_job['itemized'] = round(job.billable_total * (1+TAX_RATE), 2)
                invoice.json['debits'].append(json_job)

                if amount > Decimal(0.0):
                    print('  {:<50} {:>15} {:>15}'.format(job.name, money(amount), money(pre_tax_amount)))

                if invoice.json['is_final'] or amount > Decimal(0.0):
                    debits.append((job, amount, False))

            print('  {:<50} {:>15} {:>15}'.format('', '-'*10, '-'*10))
            print('  {:<50} {:>15} {:>15}'.format('', money(invoice_amount), money(pre_tax_invoice)))
            if round(invoice.amount, 2) != round(invoice_amount, 2):
                # i've manually checked these invoices - lex
                # for Demo project we just do the fix without checking
                if invoice.id in [31, 37, 38, 46, 47, 51, 54, 55, 56, 60, 62, 63, 67, 69, 70, 71] or company.name == 'Demo':
                    # 37, 46, 54, 55 - rounding errors, off by one penny
                    # 56, 60, 63, 69, 71 - all these had the 'balance' remaining instead of how much was actually debited
                    # 31, 38 - debit was correct but invoice had wrong amount, not sure why
                    # 67, 70 - amounts slightly off
                    # 51 - not even sure what happened here but i think the new invoice_amount is correct
                    # 62 - off by $6, probably work completed was reduced since last invoice/payment
                    invoice.amount = invoice_amount
                else:
                    raise ArithmeticError('{} != {}'.format(money(round(invoice.amount, 2)), money(round(invoice_amount, 2))))

            if invoice.json['is_final']:
                final_debits.append((invoice, debits))
            else:
                invoice.transaction = skr03.partial_debit(debits, invoice.document_date)

            invoice.json['version'] = '1.2'
            invoice.json['id'] = invoice.id
            invoice.json['title'] = invoice.json.get('title', '')
            invoice.json['debit_gross'] = invoice_amount
            invoice.json['debit_net'] = pre_tax_invoice
            invoice.json['debit_tax'] = invoice_amount - pre_tax_invoice
            invoice.json['debited_gross'] = invoice.json.pop('total_gross')
            invoice.json['debited_net'] = invoice.json.pop('total_base')
            invoice.json['debited_tax'] = invoice.json.pop('total_tax')
            invoice.json['balance_net'] = invoice.json.pop('balance_base')

            invoice.save()

        for payment in project.account.payments().all():

            transaction = payment.transaction
            entries = transaction.entries.all()
            print("\n Converting Payment Transaction #{} (entries: {}) - {}".format(transaction.id, len(entries), money(abs(payment.amount))))

            bank_entry, project_entry, promised_entry, partial_entry, tax_entry,\
                discount_entry, discount_promised_entry, cash_discount_entry = (None,)*8
            if len(entries) == 2:
                bank_entry = entries[0]
                project_entry = entries[1]
            elif len(entries) == 5:
                if entries[0].account.account_type == Account.ASSET:
                    if entries[3].account.code == "8736": # payment + discount on final invoice
                        bank_entry = entries[0]
                        project_entry = entries[1]
                        discount_entry = entries[2]
                        cash_discount_entry = entries[3]
                        tax_entry = entries[4]
                    else:
                        bank_entry = entries[0]
                        project_entry = entries[1]
                        promised_entry = entries[2]
                        partial_entry = entries[3]
                        tax_entry = entries[4]
                else: # old style
                    promised_entry = entries[0]
                    partial_entry = entries[1]
                    tax_entry = entries[2]
                    bank_entry = entries[3]
                    project_entry = entries[4]
            elif len(entries) == 7:
                if entries[0].account.account_type == Account.ASSET:
                    bank_entry = entries[0]
                    project_entry = entries[1]
                    promised_entry = entries[2]
                    partial_entry = entries[3]
                    tax_entry = entries[4]
                    discount_entry = entries[5]
                    discount_promised_entry = entries[6]
                else: # old style
                    promised_entry = entries[0]
                    partial_entry = entries[1]
                    tax_entry = entries[2]
                    bank_entry = entries[3]
                    project_entry = entries[4]
                    discount_promised_entry = entries[5]
                    discount_entry = entries[6]
            else:
                raise NotImplementedError("Dono what to do with this many entries...")

            assert bank_entry.account.account_type == Account.ASSET
            assert project_entry.account.id == project.account.id
            assert promised_entry is None or promised_entry.account.code == "1710"
            assert partial_entry is None or partial_entry.account.code == "1718"
            assert cash_discount_entry is None or cash_discount_entry.account.code == "8736"
            assert tax_entry is None or tax_entry.account.code == "1776"
            assert discount_entry is None or discount_entry.account.id == project.account.id
            assert discount_promised_entry is None or discount_promised_entry.account.code == "1710"

            if transaction.id == 121:
                # this payment is supposed to be a refund, or we're not sure
                # will need to be fixed later
                continue

            if transaction.id == 121:
                pass

            transaction.id = None  # start new transaction from previous
            transaction.transaction_type = transaction.PAYMENT
            transaction.debit(bank_entry.account, bank_entry.amount)

            # lets try paying previous invoice

            invoice = Invoice.objects.filter(project=project, document_date__lt=transaction.transacted_on).order_by('-document_date').first()
            if invoice and invoice.amount >= (bank_entry.amount+(-discount_entry.amount if discount_entry else 0)-Decimal(.01)):

                print('\n   Applying payment to previous invoice #{} - {} - {} - {}...'.format(invoice.id, invoice.invoice_no, invoice.document_date, money(invoice.amount)))

                remaining_payment_amount = payment_amount = Decimal(abs(bank_entry.amount))
                remaining_discount_amount = discount_amount = Decimal(0.0)
                discount_percent = 0.0
                if discount_entry:
                    remaining_discount_amount = discount_amount = Decimal(abs(discount_entry.amount))
                    discount_percent = round(remaining_discount_amount/(remaining_payment_amount+remaining_discount_amount), 3)

                print('\n   Discount: {} ({}%)\n'.format(money(discount_amount), round(discount_percent*100, 1)))

                job_credits_sum = Decimal(0.0)

                non_zero_debits = [debit for debit in invoice.json['debits'] if debit['debit_amount'] > 0.0]
                last_debit_idx = len(non_zero_debits)-1
                for debit_idx, debit in enumerate(non_zero_debits):

                    job = Job.objects.get(id=debit['job.id'])

                    debit_amount = Decimal(debit['debit_amount'])
                    if job.account.balance >= (remaining_payment_amount+remaining_discount_amount) <= debit_amount or \
                       last_debit_idx == debit_idx:
                        job_credit = remaining_payment_amount
                        job_discount = remaining_discount_amount
                    else:
                        if debit_amount > job.account.balance < (remaining_payment_amount+remaining_discount_amount):
                            job_credit = job.account.balance
                        else:
                            job_credit = debit_amount
                        if discount_entry:
                            job_discount = round(job_credit * discount_percent, 2)
                            job_credit -= job_discount

                    assert (job_credit+job_discount-Decimal('0.01')) <= job.account.balance

                    job_income = round(job_credit / (1 + TAX_RATE), 2)

                    job_credits_sum += job_credit

                    transaction.credit(job.account, job_credit, entry_type=Entry.PAYMENT, job=job)
                    transaction.debit(Account.objects.get(code="1710"), job_credit, job=job)
                    transaction.credit(Account.objects.get(code="1718"), job_income, job=job)
                    transaction.credit(Account.objects.get(code="1776"), round(job_credit - job_income, 2), job=job)

                    if discount_entry:
                        transaction.credit(job.account, job_discount, entry_type=Entry.DISCOUNT, job=job)
                        transaction.debit(Account.objects.get(code="1710"), job_discount, job=job)

                    remaining_payment_amount -= job_credit
                    remaining_discount_amount -= job_discount

                    if not remaining_payment_amount:
                        break

            else:

                # paying previous invoice didn't work, so lets go back to splitting the payment

                project_balance = project.balance
                sorted_jobs = [(round(job.account.balance/project_balance,3), job.account.balance, job) for job in project.jobs.all() if job.account.balance > Decimal(0.0)]
                sorted_jobs.sort()
                print('\n   Splitting payment into job accounts...')
                percent_total = Decimal(0.0)
                for job in sorted_jobs:
                    percent_total += job[0]
                    print('    {:>5}% {}'.format(round(job[0]*100, 1), job[2].name))
                print('    {:>5}'.format('-'*6))
                print('    {:>5}%\n'.format(round(percent_total*100, 1)))

                remaining_payment_amount = payment_amount = Decimal(abs(project_entry.amount))
                remaining_discount_amount = discount_amount = Decimal(0.0)
                discount_percent = 0.0
                if discount_entry:
                    remaining_discount_amount = discount_amount = Decimal(abs(discount_entry.amount))
                    discount_percent = round(remaining_discount_amount/(remaining_payment_amount+remaining_discount_amount), 3)

                print('\n   Discount: {} ({}%)\n'.format(money(discount_amount), round(discount_percent*100, 1)))

                job_credits_sum = Decimal(0.0)

                last_job_idx = len(sorted_jobs)-1
                for idx, (job_percent, job_balance, job) in enumerate(sorted_jobs):

                    # TODO: Add support final payments.

                    if idx == last_job_idx:  # use whatever is left on last job
                        assert job_balance >= (remaining_payment_amount+remaining_discount_amount)
                        job_credit = remaining_payment_amount
                        job_discount = remaining_discount_amount
                    else:
                        job_credit = round(payment_amount * job_percent, 2)
                        job_discount = round(discount_amount * job_percent, 2)
                        assert round(1-job_credit/(job_credit+job_discount), 3) == discount_percent

                    job_income = round(job_credit / (1 + TAX_RATE), 2)

                    job_credits_sum += job_credit

                    transaction.credit(job.account, job_credit, entry_type=Entry.PAYMENT, job=job)
                    transaction.debit(Account.objects.get(code="1710"), job_credit, job=job)
                    transaction.credit(Account.objects.get(code="1718"), job_income, job=job)
                    transaction.credit(Account.objects.get(code="1776"), round(job_credit - job_income, 2), job=job)

                    if discount_entry:
                        transaction.credit(job.account, job_discount, entry_type=Entry.DISCOUNT, job=job)
                        transaction.debit(Account.objects.get(code="1710"), job_discount, job=job)

                    remaining_payment_amount -= job_credit
                    remaining_discount_amount -= job_discount

            print('\n   {:<70} {:>15} {:>15}'.format('New transaction entries...', 'debits', 'credits'))
            for entry in transaction._entries:

                entry_title = entry[1].account.code+' '
                if entry[1].entry_type in [Entry.PAYMENT, Entry.DISCOUNT]:
                    entry_title += entry[1].account.job.name
                else:
                    entry_title += entry[1].account.name

                if entry[1].is_debit():
                    print('   {:<70} {:>15} {:>15}'.format(entry_title, money(abs(entry[1].amount)), ''))
                else:
                    print('   {:<70} {:>15} {:>15}'.format(entry_title, '', money(abs(entry[1].amount))))
            print('   {:<70} {:>15} {:>15}'.format('', '-'*10, '-'*10))
            print('   {:<70} {:>15} {:>15}'.format('', money(transaction._total('debit')), money(transaction._total('credit'))))

            # lets make sure we exactly used up the entire amount
            assert remaining_payment_amount == 0.0
            assert remaining_discount_amount == 0.0

            # other checks...
            assert transaction._total('debit') == payment_amount*2 + discount_amount
            assert job_credits_sum == payment_amount

            # save() also checks that all debits == all credits
            transaction.save()

        if project.id == 59:
            pass

        for invoice, debits in final_debits:
            invoice.transaction = skr03.final_debit(debits, invoice.document_date)
            invoice.save()

        # Now that we have invoices and payments migrated to the new system we can
        # generate the new transaction history tables...
        print('\n\n   Calculating transaction histories....')
        project = Project.objects.get(id=project.id)
        for invoice in project.invoices.all():
            jobs = Job.objects.filter(id__in=[debit['job.id'] for debit in invoice.json['debits']])
            invoice.json['transactions'] = get_transactions_for_jobs(jobs, invoice.document_date)
            invoice.save()

#        if not project.account.entries.exists():
#            if SHOW_SKIPPED:
#                print("")
#                print("Project #{} - {}".format(project.id,project.name))
#                print(" - No Entries -")
#            continue
#
#        table = get_transactions_table_original(project)
#
#        if len(table) < 2 or\
#                not (table[0][0] == 'debit' and table[1][0] == 'invoice'):
#            if SHOW_SKIPPED:
#                print("")
#                print("Project #{} - {}".format(project.id,project.name))
#                print(' == No initial debit/invoice. (has {} entries) == '.format(
#                    project.account.entries.count()
#                ))
#            continue
#
#        print("")
#        print("Project #{} - {}".format(project.id,project.name))
#
#        invoice_no = 1
#        payment_no = 1
#
#        for row in table:
#
#            if row[0] == 'invoice':
#
#                print(' Invoice {}'.format(invoice_no))
#                if not row[2].json:
#                    print('  !!! No json for invoice. !!!')
#                    break
#
#                transaction = Transaction()
#                total_trans = Decimal(0.0)
#                for json_job in row[2].json['jobs']:
#                    job = project.jobs.get(name=json_job['name'], job_code=int(json_job['code']))
#                    amount = Decimal(0)
#                    for json_taskgroup in json_job['taskgroups']:
#                        amount += Decimal(json_taskgroup['total'])
#                    amount *= Decimal(1.19)
#                    already_debited = round(job.account.debits().total, 2)
#                    amount -= already_debited
#                    total_trans += amount
#                    if amount > Decimal(0.0):
#                        print('  {:<50} {:>15}'.format(job.name, money(amount)))
#                        transaction.debit(job.account, amount)
#                        transaction.credit(Account.objects.get(code="1710"), amount)
#                print('  {:<50} {:>15}'.format('', money(total_trans)))
#                transaction.save()
#
#                invoice_no += 1
#
#            elif row[0] == 'payment':
#
#                payment = row[2]
#                payment_amount = payment_remaining = abs(payment.amount)
#                discount_amount = Decimal(0.0)
#                for discount in payment.transaction.discounts_to_account(project.account).all():
#                    discount_amount += discount.amount
#                discount_amount = abs(discount_amount)
#
#                discount_percent = discount_amount/payment_amount
#                print(' Payment {}: {} / {} ({}%)'.format(payment_no,
#                            money(payment_amount),
#                            money(discount_amount),
#                            round(discount_percent*100)))
#
#                payment_jobs = []
#                for job in project.jobs.all():
#                    this_payment = payment_remaining
#                    if job.account.balance <= payment_remaining:
#                        this_payment = job.account.balance
#                        payment_remaining -= job.account.balance
#                    else:
#                        payment_remaining = Decimal(0.0)
#
#                    if this_payment > Decimal(0):
#                        payment_jobs.append((job, round(this_payment, 2), discount_percent))
#                        print('  {:<50} {:>15}'.format(job.name, money(this_payment+discount_amount)))
#
#                if payment_jobs:
#                    partial_credit(payment_jobs, round(payment_amount, 2))


if __name__ == '__main__':
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
    import django
    django.setup()
    from systori.apps.accounting.utils import get_transactions_for_jobs
    from systori.apps.company.models import *
    company = Company.objects.get(schema='mehr_handwerk')
    company.activate()
    migrate_accounts(company)
