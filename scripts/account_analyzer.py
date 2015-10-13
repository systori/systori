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
    from systori.apps.accounting.models import Account, Transaction, create_account_for_job
    from systori.apps.accounting.skr03 import partial_credit
    from systori.apps.task.models import Job

    from systori.lib.templatetags.customformatting import money

    for project in Project.objects.without_template():
        project.account.code = int(project.account.code) + 1000
        project.account.save()

    for job in Job.objects.all():
        job.account = create_account_for_job(job)
        job.save()

    for project in Project.objects.without_template().order_by('id'):

        if not project.account.entries.exists():
            if SHOW_SKIPPED:
                print("")
                print("Project #{} - {}".format(project.id,project.name))
                print(" - No Entries -")
            continue

        table = get_transactions_table_original(project)

        if len(table) < 2 or\
                not (table[0][0] == 'debit' and table[1][0] == 'invoice'):
            if SHOW_SKIPPED:
                print("")
                print("Project #{} - {}".format(project.id,project.name))
                print(' == No initial debit/invoice. (has {} entries) == '.format(
                    project.account.entries.count()
                ))
            continue

        print("")
        print("Project #{} - {}".format(project.id,project.name))

        invoice_no = 1
        payment_no = 1

        for row in table:

            if row[0] == 'invoice':

                print(' Invoice {}'.format(invoice_no))
                if not row[2].json:
                    print('  !!! No json for invoice. !!!')
                    break

                transaction = Transaction()
                total_trans = Decimal(0.0)
                for json_job in row[2].json['jobs']:
                    job = project.jobs.get(name=json_job['name'], job_code=int(json_job['code']))
                    amount = Decimal(0)
                    for json_taskgroup in json_job['taskgroups']:
                        amount += Decimal(json_taskgroup['total'])
                    amount *= Decimal(1.19)
                    already_debited = round(job.account.debits().total, 2)
                    amount -= already_debited
                    total_trans += amount
                    if amount > Decimal(0.0):
                        print('  {:<50} {:>15}'.format(job.name, money(amount)))
                        transaction.debit(job.account, amount)
                        transaction.credit(Account.objects.get(code="1710"), amount)
                print('  {:<50} {:>15}'.format('', money(total_trans)))
                transaction.save()

                invoice_no += 1

            elif row[0] == 'payment':

                payment = row[2]
                payment_amount = payment_remaining = abs(payment.amount)
                discount_amount = Decimal(0.0)
                for discount in payment.transaction.discounts_to_account(project.account).all():
                    discount_amount += discount.amount
                discount_amount = abs(discount_amount)

                discount_percent = discount_amount/payment_amount
                print(' Payment {}: {} / {} ({}%)'.format(payment_no,
                            money(payment_amount),
                            money(discount_amount),
                            round(discount_percent*100)))

                payment_jobs = []
                for job in project.jobs.all():
                    this_payment = payment_remaining
                    if job.account.balance <= payment_remaining:
                        this_payment = job.account.balance
                        payment_remaining -= job.account.balance
                    else:
                        payment_remaining = Decimal(0.0)

                    if this_payment > Decimal(0):
                        payment_jobs.append((job, round(this_payment, 2), discount_percent))
                        print('  {:<50} {:>15}'.format(job.name, money(this_payment+discount_amount)))

                if payment_jobs:
                    partial_credit(payment_jobs, round(payment_amount, 2))


if __name__ == '__main__':
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
    import django
    django.setup()
    from systori.apps.company.models import *
    Company.objects.get(schema='mehr_handwerk').activate()
    migrate_accounts()
