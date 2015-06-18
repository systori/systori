def get_transactions_table(project):
    # Flatten and sort list of debits + invoices + payments
    debits = [('debit', d.transaction.recorded_on.date(), d) for d in project.account.debits().all()]
    invoices = [('invoice', i.document_date, i) for i in project.invoices.all()]
    payments = [('payment', p.received_on, p) for p in project.account.payments().all()]
    all_the_things = debits + invoices + payments
    all_the_things.sort(key=lambda i: i[1])

    # Now we add the discounts
    transactions = []
    for r_type, r_date, payment in all_the_things:
        transactions.append((r_type, r_date, payment))
        if r_type != 'payment': continue
        for discount in payment.transaction.discounts_to_account(project.account).all():
            transactions.append(('discount', r_date, discount))

    return transactions
