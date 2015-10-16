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
    from systori.apps.accounting.skr03 import partial_credit
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
                already_debited = round(job.account.debits().total, 2)

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
                if invoice.id in [31, 37, 38, 46, 47, 51, 54, 55, 56, 60]:  # i've manually checked these invoices - lex
                    # TODO WARNING: submitted github tickets about these: 47
                    # 37, 46, 54, 55 - rounding errors, off by one penny
                    # 56, 60 - all these had the 'balance' remaining instead of how much was actually debited
                    # 31, 38 - debit was correct but invoice had wrong amount, not sure why
                    # 51 - not even sure what happened here but i think the new invoice_amount is correct
                    invoice.amount = invoice_amount
                else:
                    raise ArithmeticError('{} != {}'.format(money(round(invoice.amount, 2)), money(round(invoice_amount, 2))))

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
    from systori.apps.company.models import *
    Company.objects.get(schema='mehr_handwerk').activate()
    migrate_accounts()
