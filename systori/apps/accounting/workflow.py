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


def debit_jobs(debits, transacted_on=None, recognize_revenue=False, debug=False):
    """
    Debit the customer accounts with any new work completed or just flat amount.
    Credit the promised payments account with the same amount to balance the transaction.
    """

    transacted_on = transacted_on or date.today()
    transaction = Transaction(transacted_on=transacted_on,
                              transaction_type=Transaction.INVOICE,
                              is_revenue_recognized=recognize_revenue)

    for job, debit_amount, entry_type in debits:

        assert debit_amount.gross >= 0
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

                assert prior_income.net >= 0  # only way this fails is if total refunds > total payments
                assert prior_income.tax == 0  # income should not include any tax entries

                if prior_income.net > 0:

                    # debit the partial payments account (liability), decreasing the liability
                    # (-) "good thing", product or service has been completed and delivered
                    transaction.debit(SKR03_PARTIAL_PAYMENTS_CODE, prior_income.net, job=job, value_type=Entry.NET)

                    # credit the income account (income), this increases the balance
                    # (+) "good thing", income is good
                    transaction.credit(SKR03_INCOME_CODE, prior_income.net, job=job, value_type=Entry.NET)

                # Moving Promised Payments

                # okay, not quite moving, more like clearing the promised payments
                # we'll add them into the income account a little bit later
                account_balance = job.account.balance

                # TODO: Need to look at net and tax separately instead of just the gross, it's possible
                #       for net and tax to be above or below 0 independently from each other
                if account_balance.gross > 0:
                    # reset balance, by paying it in full
                    transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, account_balance.net, job=job, value_type=Entry.NET)
                    transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, account_balance.tax, job=job, value_type=Entry.TAX)
                    transaction.credit(job.account, account_balance.net, entry_type=Entry.ADJUSTMENT, job=job, value_type=Entry.NET)
                    transaction.credit(job.account, account_balance.tax, entry_type=Entry.ADJUSTMENT, job=job, value_type=Entry.TAX)

                elif account_balance.gross < 0:
                    # we can work with a negative balance but only if there is a current debit pending
                    # that will get the account back to zero or positive (since we can't have a negative invoice)
                    assert debit_amount.gross + account_balance.gross >= 0
                    # reset balance, by refunding it in full
                    transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, account_balance.negate.net, job=job, value_type=Entry.NET)
                    transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, account_balance.negate.tax, job=job, value_type=Entry.TAX)
                    transaction.debit(job.account, account_balance.negate.net, entry_type=Entry.ADJUSTMENT, job=job, value_type=Entry.NET)
                    transaction.debit(job.account, account_balance.negate.tax, entry_type=Entry.ADJUSTMENT, job=job, value_type=Entry.TAX)

                # update the new debit increasing or decreasing it depending on the balance
                debit_amount += account_balance

                # Now we can mark ourselves as revenue recognized for a job well done! Pun intended.
                job.is_revenue_recognized = True
                job.save()

            if debit_amount.gross > 0:

                # debit the customer account (asset), this increases their balance
                # (+) "good thing", customer owes us more money
                transaction.debit(job.account, debit_amount.net, entry_type=entry_type, job=job, value_type=Entry.NET)
                transaction.debit(job.account, debit_amount.tax, entry_type=entry_type, job=job, value_type=Entry.TAX)

                # credit the tax payments account (liability), increasing the liability
                # (+) "bad thing", will have to be paid in taxes eventually
                if debit_amount.tax > 0:  # when the refund is very small (like 0.01) there is no tax
                    transaction.credit(SKR03_TAX_PAYMENTS_CODE, debit_amount.tax, job=job, value_type=Entry.TAX)

                # credit the income account (income), this increases the balance
                # (+) "good thing", income is good
                transaction.credit(SKR03_INCOME_CODE, debit_amount.net, job=job, value_type=Entry.NET)

        else:
            # Still not recognizing revenue, tracking debits in a promised payments account instead..

            if debit_amount.gross > 0:

                # debit the customer account (asset), this increases their balance
                # (+) "good thing", customer owes us more money
                if debit_amount.net > 0:
                    transaction.debit(job.account, debit_amount.net, entry_type=entry_type, job=job, value_type=Entry.NET)
                if debit_amount.tax > 0:
                    transaction.debit(job.account, debit_amount.tax, entry_type=entry_type, job=job, value_type=Entry.TAX)

                # credit the promised payments account (liability), increasing the liability
                # (+) "bad thing", customer owing us money is a liability
                if debit_amount.net > 0:
                    transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, debit_amount.net, job=job, value_type=Entry.NET)
                if debit_amount.tax > 0:
                    transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, debit_amount.tax, job=job, value_type=Entry.TAX)

    transaction.save(debug=debug)

    return transaction


def credit_jobs(splits, payment, transacted_on=None, bank=None, debug=False):
    """ Applies a payment or adjustment. """

    assert isinstance(payment, Decimal)
    assert payment == sum([p[1].gross for p in splits])

    bank = bank or Account.objects.get(code=SKR03_BANK_CODE)
    transacted_on = transacted_on or date.today()

    transaction = Transaction(transacted_on=transacted_on, transaction_type=Transaction.PAYMENT)

    # debit the bank account (asset)
    # (+) "good thing", money in the bank is always good
    if payment > 0:
        transaction.debit(bank, payment, value_type=Entry.GROSS)

    for (job, amount, discount, adjustment) in splits:

        if amount.gross > 0:

            # credit the customer account (asset), decreasing their balance
            # (-) "bad thing", customer owes us less money
            transaction.credit(job.account, amount.net, entry_type=Entry.PAYMENT, job=job, value_type=Entry.NET)
            if amount.tax > 0:
                transaction.credit(job.account, amount.tax, entry_type=Entry.PAYMENT, job=job, value_type=Entry.TAX)

            if not job.is_revenue_recognized:

                # debit the promised payments account (liability), decreasing the liability
                # (-) "good thing", customer paying debt reduces liability
                transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, amount.net, job=job, value_type=Entry.NET)
                if amount.tax > 0:
                    transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, amount.tax, job=job, value_type=Entry.TAX)

                # credit the partial payments account (liability), increasing the liability
                # (+) "bad thing", we are on the hook to finish and deliver the service or product
                transaction.credit(SKR03_PARTIAL_PAYMENTS_CODE, amount.net, job=job, value_type=Entry.NET)

                # credit the tax payments account (liability), increasing the liability
                # (+) "bad thing", tax have to be paid eventually
                if amount.tax > 0:
                    transaction.credit(SKR03_TAX_PAYMENTS_CODE, amount.tax, job=job, value_type=Entry.TAX)

        for reduction_type, reduction in [(Entry.DISCOUNT, discount), (Entry.ADJUSTMENT, adjustment)]:

            if reduction.gross > 0:

                # credit the customer account (asset), decreasing their balance
                # (-) "bad thing", customer owes us less money
                transaction.credit(job.account, reduction.net, entry_type=reduction_type, job=job, value_type=Entry.NET)
                if reduction.tax > 0:
                    transaction.credit(job.account, reduction.tax, entry_type=reduction_type, job=job, value_type=Entry.TAX)

                if job.is_revenue_recognized:
                    # Reduction after final invoice has a few more steps involved.

                    if reduction_type == Entry.DISCOUNT:
                        # debit the cash discount account (income), indirectly subtracts from the income
                        # (-) "bad thing", less income :-(
                        transaction.debit(SKR03_CASH_DISCOUNT_CODE, reduction.net, job=job, value_type=Entry.NET)

                    elif reduction_type == Entry.ADJUSTMENT:
                        # debit the income account (income), this decreases the balance
                        # (+) "bad thing", loss in income :-(
                        transaction.debit(SKR03_INCOME_CODE, reduction.net, job=job, value_type=Entry.NET)

                    # debit the tax payments account (liability), decreasing the liability
                    # (-) "good thing", less taxes to pay
                    if reduction.tax > 0:
                        transaction.debit(SKR03_TAX_PAYMENTS_CODE, reduction.tax, job=job, value_type=Entry.TAX)

                else:
                    # Reduction prior to final invoice is simpler.

                    # debit the promised payments account (liability), decreasing the liability
                    # (-) "good thing", customer paying debt reduces liability
                    transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, reduction.net, job=job, value_type=Entry.NET)
                    if reduction.tax > 0:
                        transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, reduction.tax, job=job, value_type=Entry.TAX)

    transaction.save(debug=debug)

    return transaction


def adjust_jobs(jobs, transacted_on=None, debug=False):

    transacted_on = transacted_on or date.today()

    transaction = Transaction(transacted_on=transacted_on, transaction_type=Transaction.ADJUSTMENT)

    for job, adjustment in jobs:

        if adjustment.net != 0:

            transaction.signed(job.account, adjustment.net, value_type=Entry.NET, entry_type=Entry.ADJUSTMENT, job=job)

            if job.is_revenue_recognized:
                transaction.signed(SKR03_INCOME_CODE, adjustment.net, value_type=Entry.NET, job=job)
            else:
                transaction.signed(SKR03_PROMISED_PAYMENTS_CODE, adjustment.net, value_type=Entry.NET, job=job)

        if adjustment.tax != 0:

            transaction.signed(job.account, adjustment.tax, value_type=Entry.TAX, entry_type=Entry.ADJUSTMENT, job=job)

            if job.is_revenue_recognized:
                transaction.signed(SKR03_TAX_PAYMENTS_CODE, adjustment.tax, value_type=Entry.TAX, job=job)
            else:
                transaction.signed(SKR03_PROMISED_PAYMENTS_CODE, adjustment.tax, value_type=Entry.TAX, job=job)

    transaction.save(debug=debug)

    return transaction


def refund_jobs(jobs, transacted_on=None, bank=None, debug=False):

    bank = bank or Account.objects.get(code=SKR03_BANK_CODE)
    transacted_on = transacted_on or date.today()

    transaction = Transaction(transacted_on=transacted_on, transaction_type=Transaction.REFUND)

    bank_refund = Decimal('0.00')

    for job, refund, refund_credit in jobs:

        if refund.gross > 0:

            bank_refund += refund.gross

            # debit the customer account (asset), this increases their balance
            # (+) "good thing", customer owes us money again
            if refund.net > 0:
                transaction.debit(job.account, refund.net, entry_type=Entry.REFUND, job=job, value_type=Entry.NET)
            if refund.tax > 0:
                transaction.debit(job.account, refund.tax, entry_type=Entry.REFUND, job=job, value_type=Entry.TAX)

            if not job.is_revenue_recognized:

                # credit the promised payments account (liability), increasing the liability
                # (+) "bad thing", customer owing us money is a liability
                if refund.net > 0:
                    transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, refund.net, job=job, value_type=Entry.NET)
                if refund.tax > 0:
                    transaction.credit(SKR03_PROMISED_PAYMENTS_CODE, refund.tax, job=job, value_type=Entry.TAX)

                # debit the partial payments account (liability), decreasing the liability
                # (-) "good thing", product or service has been completed and delivered
                if refund.net > 0:
                    transaction.debit(SKR03_PARTIAL_PAYMENTS_CODE, refund.net, job=job, value_type=Entry.NET)

                # debit the tax payments account (liability), decreasing the liability
                # (-) "good thing", less taxes to pay
                if refund.tax > 0:
                    transaction.debit(SKR03_TAX_PAYMENTS_CODE, refund.tax, job=job, value_type=Entry.TAX)

        if refund_credit.gross > 0:

            bank_refund -= refund_credit.gross

            # credit the customer account (asset), decreasing their balance
            # (-) "bad thing", customer owes us less money
            transaction.credit(job.account, refund_credit.net, entry_type=Entry.REFUND_CREDIT, job=job, value_type=Entry.NET)
            if refund_credit.tax > 0:
                transaction.credit(job.account, refund_credit.tax, entry_type=Entry.REFUND_CREDIT, job=job, value_type=Entry.TAX)

            if not job.is_revenue_recognized:

                # debit the promised payments account (liability), decreasing the liability
                # (-) "good thing", customer paying debt reduces liability
                transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, refund_credit.net, job=job, value_type=Entry.NET)
                if refund_credit.tax > 0:
                    transaction.debit(SKR03_PROMISED_PAYMENTS_CODE, refund_credit.tax, job=job, value_type=Entry.TAX)

                # credit the partial payments account (liability), increasing the liability
                # (+) "bad thing", we are on the hook to finish and deliver the service or product
                transaction.credit(SKR03_PARTIAL_PAYMENTS_CODE, refund_credit.net, job=job, value_type=Entry.NET)

                # credit the tax payments account (liability), increasing the liability
                # (+) "bad thing", tax have to be paid eventually
                if refund_credit.tax > 0:
                    transaction.credit(SKR03_TAX_PAYMENTS_CODE, refund_credit.tax, job=job, value_type=Entry.TAX)

    assert bank_refund >= 0  # check that we haven't applied more than we refunded

    # credit the bank account (asset)
    # (-) "bad thing", money leaving the bank
    if bank_refund > 0:
        transaction.credit(bank, bank_refund, value_type=Entry.GROSS)

    transaction.save(debug=debug)

    return transaction


def create_chart_of_accounts(self=None):
    if not self: self = type('', (), {})()

    self.promised_payments = Account.objects.create(name="Promised Payments", account_type=Account.LIABILITY, code=SKR03_PROMISED_PAYMENTS_CODE)
    self.partial_payments = Account.objects.create(name="Partial Payments", account_type=Account.LIABILITY, code=SKR03_PARTIAL_PAYMENTS_CODE)
    self.tax_payments = Account.objects.create(name="Tax Payments", account_type=Account.LIABILITY, code=SKR03_TAX_PAYMENTS_CODE)

    self.income = Account.objects.create(name="Income", account_type=Account.INCOME, code=SKR03_INCOME_CODE)
    self.cash_discount = Account.objects.create(name="Cash Discount", account_type=Account.INCOME, code=SKR03_CASH_DISCOUNT_CODE)

    self.bank = Account.objects.create(name="Default Bank Account", account_type=Account.ASSET, asset_type=Account.BANK, code=SKR03_BANK_CODE)
