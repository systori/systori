from datetime import date
from systori.lib.accounting.tools import compute_gross_tax, extract_net_tax
from .models import *
from .constants import *


# Reading material for double entry accounting:
# http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
# http://www.find-uk-accountant.co.uk/articles/fua/16
# http://www.accountingcoach.com/accounts-receivable-and-bad-debts-expense/explanation
# http://www.ledger-cli.org/3.0/doc/ledger3.html

# Completed Contract Accounting Method
# https://en.wikipedia.org/wiki/Completed-contract_method

# Revenue Recognition
# https://en.wikipedia.org/wiki/Revenue_recognition


def debit_jobs(debits, transacted_on=None, recognize_revenue=False):
    """
    Debit the customer accounts with any new work completed or just flat amount.
    Credit the promised payments account with the same amount to balance the transaction.
    """

    transacted_on = transacted_on or date.today()
    transaction = Transaction(transacted_on=transacted_on,
                              transaction_type=Transaction.INVOICE,
                              is_revenue_recognized=recognize_revenue)

    for job, debit_amount, entry_type in debits:

        assert debit_amount >= 0
        assert entry_type in (Entry.WORK_DEBIT, Entry.FLAT_DEBIT)

        if recognize_revenue or job.is_revenue_recognized:
            # we're creating a final invoice or this job was already on a final invoice before

            if not job.is_revenue_recognized:
                # this job wasn't on any final invoices before, so we're switching
                # from delayed revenue recognition to recognized revenue and
                # this means we need to move all of the built-up partial payments and promised payments
                # into the revenue account

                # Moving Partial Payments

                partial_payments_account = Account.objects.get(code=SKR03_PARTIAL_PAYMENTS_CODE)
                prior_income = partial_payments_account.entries.filter(job=job).sum

                assert prior_income >= 0  # only way this fails is if total refunds > total payments

                if prior_income > 0:

                    # debit the partial payments account (liability), decreasing the liability
                    # (-) "good thing", product or service has been completed and delivered
                    transaction.debit(SKR03_PARTIAL_PAYMENTS_CODE, prior_income, job=job, tax_rate=TAX_RATE)

                    # credit the income account (income), this increases the balance
                    # (+) "good thing", income is good
                    transaction.credit(SKR03_INCOME_CODE, prior_income, job=job, tax_rate=TAX_RATE)

                # Moving Promised Payments

                # okay, not quite moving, more like clearing the promised payments
                # we'll add them into the income account a little bit later
                account_balance = job.account.balance

                if account_balance > 0:
                    # reset balance, by paying it in full
                    transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, account_balance, job=job, tax_rate=TAX_RATE)
                    transaction.credit(job.account, account_balance, job=job, tax_rate=TAX_RATE)

                elif account_balance < 0:
                    # we can work with a negative balance but only if there is a current debit pending
                    # that will get the account back to zero or positive (since we can't have a negative invoice)
                    assert debit_amount + account_balance >= 0
                    # reset balance, by refunding it in full
                    transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, abs(account_balance), job=job, tax_rate=TAX_RATE)
                    transaction.debit(job.account, abs(account_balance), job=job, tax_rate=TAX_RATE)

                # update the new debit increasing or decreasing it depending on the balance
                debit_amount += account_balance

                # Now we can mark ourselves as revenue recognized for a job well done! Pun intended.
                job.is_revenue_recognized = True
                job.save()

            if debit_amount > 0:

                income, tax = extract_net_tax(debit_amount, TAX_RATE)

                # debit the customer account (asset), this increases their balance
                # (+) "good thing", customer owes us more money
                transaction.debit(job.account, debit_amount, entry_type=entry_type, job=job, tax_rate=TAX_RATE)

                # credit the tax payments account (liability), increasing the liability
                # (+) "bad thing", will have to be paid in taxes eventually
                if tax > 0:  # when the refund is very small (like 0.01) there is no tax
                    transaction.credit(SKR03_TAX_PAYMENTS_CODE, tax, job=job)

                # credit the income account (income), this increases the balance
                # (+) "good thing", income is good
                transaction.credit(SKR03_INCOME_CODE, income, job=job)

        else:
            # Still not recognizing revenue, tracking debits in a promised payments account instead..

            if debit_amount > 0:

                # debit the customer account (asset), this increases their balance
                # (+) "good thing", customer owes us more money
                transaction.debit(job.account, debit_amount, entry_type=entry_type, job=job, tax_rate=TAX_RATE)

                # credit the promised payments account (liability), increasing the liability
                # (+) "bad thing", customer owing us money is a liability
                transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, debit_amount, job=job, tax_rate=TAX_RATE)

    transaction.save()

    return transaction


def credit_jobs(splits, payment, transacted_on=None, bank=None):
    """ Applies a payment or adjustment. """

    assert isinstance(payment, Decimal)
    assert payment == sum([p[1] for p in splits])

    bank = bank or Account.objects.get(code=SKR03_BANK_CODE)
    transacted_on = transacted_on or date.today()

    transaction = Transaction(transacted_on=transacted_on, transaction_type=Transaction.PAYMENT)

    # debit the bank account (asset)
    # (+) "good thing", money in the bank is always good
    if payment > 0:
        transaction.debit(bank, payment)

    for (job, gross, discount, adjustment) in splits:

        if gross > 0:

            # credit the customer account (asset), decreasing their balance
            # (-) "bad thing", customer owes us less money
            transaction.credit(job.account, gross, entry_type=Entry.PAYMENT, job=job, tax_rate=TAX_RATE)

            if not job.is_revenue_recognized:
                # extract the income and tax part from the payment
                net, tax = extract_net_tax(gross, TAX_RATE)

                # debit the promised payments account (liability), decreasing the liability
                # (-) "good thing", customer paying debt reduces liability
                transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, gross, job=job, tax_rate=TAX_RATE)

                # credit the partial payments account (liability), increasing the liability
                # (+) "bad thing", we are on the hook to finish and deliver the service or product
                transaction.credit(SKR03_PARTIAL_PAYMENTS_CODE, net, job=job)

                # credit the tax payments account (liability), increasing the liability
                # (+) "bad thing", tax have to be paid eventually
                transaction.credit(SKR03_TAX_PAYMENTS_CODE, tax, job=job)

        for reduction_type, reduction in [(Entry.DISCOUNT, discount), (Entry.ADJUSTMENT, adjustment)]:

            if reduction > 0:

                # credit the customer account (asset), decreasing their balance
                # (-) "bad thing", customer owes us less money
                transaction.credit(job.account, reduction, entry_type=reduction_type, job=job, tax_rate=TAX_RATE)

                if job.is_revenue_recognized:
                    # Reduction after final invoice has a few more steps involved.

                    reduction_net, reduction_tax = extract_net_tax(reduction, TAX_RATE)

                    if reduction_type == Entry.DISCOUNT:
                        # debit the cash discount account (income), indirectly subtracts from the income
                        # (-) "bad thing", less income :-(
                        transaction.debit(SKR03_CASH_DISCOUNT_CODE, reduction_net, job=job)

                    elif reduction_type == Entry.ADJUSTMENT:
                        # debit the income account (income), this decreases the balance
                        # (+) "bad thing", loss in income :-(
                        transaction.debit(SKR03_INCOME_CODE, reduction_net, job=job)

                    # debit the tax payments account (liability), decreasing the liability
                    # (-) "good thing", less taxes to pay
                    transaction.debit(SKR03_TAX_PAYMENTS_CODE, reduction_tax, job=job)

                else:
                    # Reduction prior to final invoice is simpler.

                    # debit the promised payments account (liability), decreasing the liability
                    # (-) "good thing", customer paying debt reduces liability
                    transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, reduction, job=job, tax_rate=TAX_RATE)

    transaction.save()


def refund_jobs(refunded, applied, transacted_on=None, bank=None):

    bank = bank or Account.objects.get(code=SKR03_BANK_CODE)
    transacted_on = transacted_on or date.today()

    transaction = Transaction(transacted_on=transacted_on, transaction_type=Transaction.REFUND)

    issued_refund = Decimal('0.00')

    for job, refund in refunded:

        issued_refund += refund

        net, tax = extract_net_tax(refund, TAX_RATE)

        # debit the customer account (asset), this increases their balance
        # (+) "good thing", customer owes us money again
        transaction.debit(job.account, refund, entry_type=Entry.REFUND_DEBIT, job=job, tax_rate=TAX_RATE)

        if not job.is_revenue_recognized:

            # credit the promised payments account (liability), increasing the liability
            # (+) "bad thing", customer owing us money again is a liability
            transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, refund, job=job, tax_rate=TAX_RATE)

            # debit the partial payments account (liability), decreasing the liability
            # (-) "good thing", no longer liable for the refunded amount in terms of taxes
            transaction.debit(SKR03_PARTIAL_PAYMENTS_CODE, net, job=job)

            # debit the tax payments account (liability), decreasing the liability
            # (-) "good thing", less taxes to pay
            if tax > 0:  # when the refund is very small (like 0.01) there is no tax
                transaction.debit(SKR03_TAX_PAYMENTS_CODE, tax, job=job)

    for job, apply in applied:

        issued_refund -= apply

        net, tax = extract_net_tax(apply, TAX_RATE)

        # credit the customer account (asset), decreasing their balance
        # (-) "bad thing", customer owes us less money
        transaction.credit(job.account, apply, entry_type=Entry.REFUND_CREDIT, job=job, tax_rate=TAX_RATE)

        if not job.is_revenue_recognized:

            # debit the promised payments account (liability), decreasing the liability
            # (-) "good thing", customer paying debt reduces liability
            transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, apply, job=job, tax_rate=TAX_RATE)

            # credit the partial payments account (liability), increasing the liability
            # (+) "bad thing", we are on the hook to finish and deliver the service or product
            transaction.credit(SKR03_PARTIAL_PAYMENTS_CODE, net, job=job)

            # credit the tax payments account (liability), increasing the liability
            # (+) "bad thing", tax have to be paid eventually
            transaction.credit(SKR03_TAX_PAYMENTS_CODE, tax, job=job)

    # credit the bank account (asset)
    # (-) "bad thing", money leaving the bank
    if issued_refund > 0:
        transaction.credit(bank, issued_refund)

    transaction.save()

    return transaction


def create_chart_of_accounts(self=None):
    if not self: self = type('', (), {})()

    self.promised_payments = Account.objects.create(account_type=Account.LIABILITY, code=SKR03_PROMISED_PAYMENTS_CODE)
    self.partial_payments = Account.objects.create(account_type=Account.LIABILITY, code=SKR03_PARTIAL_PAYMENTS_CODE)
    self.tax_payments = Account.objects.create(account_type=Account.LIABILITY, code=SKR03_TAX_PAYMENTS_CODE)

    self.income = Account.objects.create(account_type=Account.INCOME, code=SKR03_INCOME_CODE)
    self.cash_discount = Account.objects.create(account_type=Account.INCOME, code=SKR03_CASH_DISCOUNT_CODE)

    self.bank = Account.objects.create(account_type=Account.ASSET, asset_type=Account.BANK, code=SKR03_BANK_CODE)
