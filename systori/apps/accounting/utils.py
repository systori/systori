def get_transactions_table(project):
    # Flatten and sort list of debits + invoices + payments
    debits = []
    invoices = [('invoice', i.document_date, i, None) for i in project.invoices.all()]
    payments = []
    for job in project.jobs.all():
        debits.extend([('debit', d.transaction.recorded_on.date(), d, job) for d in job.account.debits().all()])
        payments.extend([('payment', p.received_on, p, job) for p in job.account.payments().all()])
    all_the_things = debits + invoices + payments
    all_the_things.sort(key=lambda i: i[1])

    # Now we add the discounts
    transactions = []
    for r_type, r_date, payment, job in all_the_things:
        transactions.append((r_type, r_date, payment, job))
        if r_type != 'payment': continue
        for discount in payment.transaction.discounts_to_account(job.account).all():
            transactions.append(('discount', r_date, discount, job))

    return transactions
