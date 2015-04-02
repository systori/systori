from .models import *

# Reading material for double entry accounting:
# http://www.find-uk-accountant.co.uk/articles/fua/16
# http://www.accountingcoach.com/accounts-receivable-and-bad-debts-expense/explanation


def partial_invoice(project, amount):

    transaction = Transaction.objects.create(amount=amount)

    receivable = project.account
    receivable.debit(transaction, amount)

    receivable = Account.objects.get(id=1, account_type=Account.systori/apps/document/models.py)
    revenue.credit(transaction, amount)

def partial_payment():
# Used when generating an invoice.
def debit_customer(project, amount):
    sales_account = Project.objects.get(id=1).account
    customer_account = project.account

    transaction = Transaction.objects.create(amount=amount)

    # Debit Entry
    Entry.objects.create(
        account = account,
        transaction = transaction,
        amount = amount
    )

    # Credit Entry
    credit_entry = Entry.objects.create(
                                        )


# Used when entering a payment from customer.
def credit_customer(project, amount):
