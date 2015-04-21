from datetime import date
from .models import *
from .constants import *


# Reading material for double entry accounting:
# http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
# http://www.find-uk-accountant.co.uk/articles/fua/16
# http://www.accountingcoach.com/accounts-receivable-and-bad-debts-expense/explanation
# http://www.ledger-cli.org/3.0/doc/ledger3.html


DEBTOR_CODE_RANGE = (10000, 69999)

BANK_CODE_RANGE = (1200, 1288)


def create_chart_of_accounts(self=None):
    if not self: self = type('',(),{})()

    self.promised_payments = Account.objects.create(account_type=Account.LIABILITY, code="1710")
    self.partial_payments = Account.objects.create(account_type=Account.LIABILITY, code="1718")
    self.tax_payments = Account.objects.create(account_type=Account.LIABILITY, code="1776")

    self.income = Account.objects.create(account_type=Account.INCOME, code="8400")

    self.bank = Account.objects.create(account_type=Account.ASSET, code="1200")


def partial_debit(project):
    """ Attempts to debit the customer account with any new work that was done since last debit. """

    amount = project.new_amount_to_debit

    if not amount: return

    transaction = Transaction()
    transaction.debit(project.account, amount) # debit the customer
    transaction.credit(Account.objects.get(code="1710"), amount)
    transaction.save()


def partial_credit(projects, payment, received_on=None, bank=None):
    """ Applies a payment to a list of customer accounts. Including discounts on a per account basis. """

    assert isinstance(payment, Decimal)

    if bank is None: bank = Account.objects.get(code="1200")
    if received_on is None: received_on = date.today()

    income = round(payment / (1+TAX_RATE), 2)

    transaction = Transaction()

    transaction.debit(Account.objects.get(code="1710"), payment, received_on=received_on)
    transaction.credit(Account.objects.get(code="1718"), income, received_on=received_on)
    transaction.credit(Account.objects.get(code="1776"), payment - income, received_on=received_on)

    transaction.debit(bank, payment)
    for (project, credit, is_discounted) in projects:
        transaction.credit(project.account, credit, is_payment=True, received_on=received_on) # credit the customer

    for (project, credit, is_discounted) in projects:

        if is_discounted:

            pre_discount_credit = round(credit / (1-DISCOUNT), 2) # undo the discount to get original amount invoiced
            discount = pre_discount_credit - credit

            transaction.debit(Account.objects.get(code="1710"), discount, received_on=received_on)
            transaction.credit(project.account, discount, is_discount=True, received_on=received_on)

    transaction.save()


def final_debit(project):
    """ Similar to partial_debit but also handles a lot of different accounting situations to prepare
        customer's account for final invoice generation.
    """

    transaction = Transaction()

    unpaid_amount = project.account.balance
    if unpaid_amount > 0:
        # reset balance, we'll add unpaid_amount back into a final debit to customer
        transaction.debit(Account.objects.get(code="1710"), unpaid_amount)
        transaction.credit(project.account, unpaid_amount)

    new_amount = project.new_amount_to_debit
    amount = new_amount + unpaid_amount
    income = round(amount / (1+TAX_RATE), 2)

    transaction.debit(project.account, amount)
    transaction.credit(Account.objects.get(code="8400"), income)
    transaction.credit(Account.objects.get(code="1776"), amount-income)


    payments = project.account.payments().total

    if payments:

        pre_tax_payments = round(payments * -1 / (1+TAX_RATE), 2)

        transaction.debit(Account.objects.get(code="1718"), pre_tax_payments)
        transaction.credit(Account.objects.get(code="8400"), pre_tax_payments)

    transaction.save()
