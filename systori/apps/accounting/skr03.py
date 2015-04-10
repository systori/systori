from .models import *

# Reading material for double entry accounting:
# http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
# http://www.find-uk-accountant.co.uk/articles/fua/16
# http://www.accountingcoach.com/accounts-receivable-and-bad-debts-expense/explanation
# http://www.ledger-cli.org/3.0/doc/ledger3.html


def new_amount_to_bill(project):
    billable = project.billable_total * Decimal(1.19)
    billed = project.account.debits_total
    return billable - billed


def partial_invoice(project):

    amount = new_amount_to_bill(project)

    transaction = Transaction()
    transaction.debit(project.account, amount)
    transaction.credit(Account.objects.get(code="1710"), amount)
    transaction.save()


def partial_payment(project, amount):

    income = amount / Decimal(1.19)

    transaction = Transaction()
    transaction.debit(Account.objects.get(code="1710"), amount)
    transaction.credit(Account.objects.get(code="1718"), income)
    transaction.credit(Account.objects.get(code="1776"), amount-income)
    transaction.save()

    transaction = Transaction()
    transaction.credit(project.account, amount)
    transaction.debit(Account.objects.get(code="1200"), amount)
    transaction.save()


def final_invoice(project):

    amount = new_amount_to_bill(project)

    transaction = Transaction()
    transaction.debit(project.account, amount)
    transaction.credit(Account.objects.get(code="1710"), amount)
    transaction.save()