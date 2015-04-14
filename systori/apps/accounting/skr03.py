from .models import *
from .constants import *


# Reading material for double entry accounting:
# http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
# http://www.find-uk-accountant.co.uk/articles/fua/16
# http://www.accountingcoach.com/accounts-receivable-and-bad-debts-expense/explanation
# http://www.ledger-cli.org/3.0/doc/ledger3.html


def new_amount_to_debit(project):
    """ This function returns the amount that can be debited to the customers
        account based on work done since the last time the customer account was debited.
    """

    # total cost of all complete work so far (with tax)
    billable = round(project.billable_total * (1+TAX_RATE), 2)

    # total we have already charged the customer
    already_debited = round(project.account.debits().total, 2)

    return billable - already_debited


def partial_debit(project):
    """ Checks to see if any work has been done on the project and thus there is something to charge the customer:
        A) Charges (debits) the customer account and returns True if there was something to charge.
        B) Does nothing and returns False if there was nothing to charge.
    """

    amount = new_amount_to_debit(project)
    
    if not amount: return False

    transaction = Transaction()
    transaction.debit(project.account, amount) # debit the customer
    transaction.credit(Account.objects.get(code="1710"), amount)
    transaction.save()
    
    return True


def partial_credit(project, payment, was_discount_applied=False):
    """ Properly applies (credits) a customers payment to their account. Handles discount situation
        when was_discount_applied argument is supplied.
    """
    assert isinstance(payment, Decimal)

    income = round(payment / (1+TAX_RATE), 2)

    # full_payment is the payment that would have been made if discount hadn't been applied
    pre_discount_payment = payment
    if was_discount_applied:
        pre_discount_payment = round(payment / (1-DISCOUNT), 2) # undo the discount to get original amount invoiced

    transaction = Transaction()
    transaction.debit(Account.objects.get(code="1710"), pre_discount_payment)
    transaction.credit(Account.objects.get(code="1718"), income)
    transaction.credit(Account.objects.get(code="1776"), payment-income)
    if payment < pre_discount_payment: # credit customer's account with the discount
        transaction.credit(project.account, pre_discount_payment-payment, is_discount=True)
    transaction.save()

    transaction = Transaction()
    transaction.credit(project.account, payment) # credit the customer
    transaction.debit(Account.objects.get(code="1200"), payment)
    transaction.save()


def final_debit(project):
    """ Similar to partial_debit but also handles a lot of different accounting situations to prepare
        customer's account for final invoice generation.
    """

    new_amount = new_amount_to_debit(project)
    unpaid_amount = project.account.balance
    amount = new_amount + unpaid_amount
    income = round(new_amount / (1+TAX_RATE), 2)

    transaction = Transaction()
    transaction.debit(project.account, new_amount)
    transaction.credit(Account.objects.get(code="8400"), income)
    transaction.credit(Account.objects.get(code="1776"), new_amount-income)
    transaction.save()

    # all credits that have already been applied towards the total bill
    credits = project.account.credits().total

    if credits:

        pre_tax_credits = round(credits / (1+TAX_RATE), 2)

        payments = project.account.payments().total * -1
        pre_tax_payments = round(payments / (1+TAX_RATE), 2)
        discounts = project.account.discounts().total * -1
        pre_tax_discounts = round(discounts / (1+TAX_RATE), 2)

        # payment credits + discount credits should equal total credits
        assert pre_tax_payments + pre_tax_discounts == pre_tax_credits

        transaction = Transaction()
        transaction.credit(Account.objects.get(code="8400"), pre_tax_credits)
        transaction.debit(Account.objects.get(code="1718"), pre_tax_payments)
        if pre_tax_discounts:
            transaction.debit(Account.objects.get(code="8736"), pre_tax_discounts)
        transaction.save()