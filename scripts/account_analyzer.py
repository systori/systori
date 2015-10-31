from decimal import Decimal


def get_transactions_table_original(project):
    debits = [('debit', d.transaction.recorded_on.date(), d) for d in project.account.debits().all()]
    invoices = [('invoice', i.document_date, i) for i in project.invoices.all()]
    payments = [('payment', p.transaction.received_on, p) for p in project.account.payments().all()]
    all_the_things = debits + invoices + payments
    all_the_things.sort(key=lambda i: i[1])
    return all_the_things


SHOW_SKIPPED = False


def migrate_accounts():
    from systori.apps.project.models import Project
    from systori.apps.accounting.models import Account, Transaction, Entry, create_account_for_job
    from systori.apps.accounting.constants import TAX_RATE
    from systori.apps.task.models import Job

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

            print("\n Invoice #{} - {}".format(invoice.id, invoice.invoice_no))
            invoice_amount = Decimal(0.0)
            pre_tax_invoice = Decimal(0.0)

            for json_job in invoice.json.get('jobs', []):

                job = project.jobs.get(name=json_job['name'], job_code=int(json_job['code']))

                pre_tax_amount = Decimal(0.0)
                for json_taskgroup in json_job['taskgroups']:
                    pre_tax_amount += Decimal(json_taskgroup['total'])

                amount = round(pre_tax_amount * Decimal(1.19), 2)
                already_debited = job.account.debits().total

                amount -= already_debited

                invoice_amount += amount
                pre_tax_invoice += pre_tax_amount

                if amount > Decimal(0.0):
                    transaction = Transaction(recorded_on=invoice.created_on, invoice=invoice)
                    transaction.debit(job.account, amount, entry_type=Entry.WORK_DEBIT)
                    transaction.credit(Account.objects.get(code="1710"), amount)
                    transaction.save()
                    print('  {:<50} {:>15} {:>15}'.format(job.name, money(amount), money(pre_tax_amount)))

            print('  {:<50} {:>15} {:>15}'.format('', '-'*10, '-'*10))
            print('  {:<50} {:>15} {:>15}'.format('', money(invoice_amount), money(pre_tax_invoice)))
            if round(invoice.amount, 2) != round(invoice_amount, 2):
                if invoice.id in [31, 37, 38, 46, 47, 51, 54, 55, 56, 60, 63, 67]:  # i've manually checked these invoices - lex
                    # TODO WARNING: submitted github tickets about these: 47
                    # 37, 46, 54, 55 - rounding errors, off by one penny
                    # 56, 60, 63 - all these had the 'balance' remaining instead of how much was actually debited
                    # 31, 38 - debit was correct but invoice had wrong amount, not sure why
                    # 67 - amounts slightly off
                    # 51 - not even sure what happened here but i think the new invoice_amount is correct
                    invoice.amount = invoice_amount
                else:
                    raise ArithmeticError('{} != {}'.format(money(round(invoice.amount, 2)), money(round(invoice_amount, 2))))

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

            transaction.id = None  # start new transaction from previous
            transaction.debit(bank_entry.account, bank_entry.amount)

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
                # TODO: Add entry groupings per job.

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

                transaction.credit(job.account, job_credit, entry_type=Entry.PAYMENT)
                transaction.debit(Account.objects.get(code="1710"), job_credit)
                transaction.credit(Account.objects.get(code="1718"), job_income)
                transaction.credit(Account.objects.get(code="1776"), round(job_credit - job_income, 2))

                if discount_entry:
                    transaction.credit(job.account, job_discount, entry_type=Entry.DISCOUNT)
                    transaction.debit(Account.objects.get(code="1710"), job_discount)

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
    from systori.apps.company.models import *
    Company.objects.get(schema='mehr_handwerk').activate()
    migrate_accounts()
