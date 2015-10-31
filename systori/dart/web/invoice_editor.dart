import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


class JobTable extends TableElement {
    TableCellElement estimate_total;
    TableCellElement itemized_total;
    TableCellElement debit_total;
    TableCellElement debited_total;
    TableCellElement balance_total;

    JobTable.created() : super.created() {
        TableRowElement totals = this.querySelector(":scope tr.job-table-totals");
        this.estimate_total = totals.querySelector(":scope>.job-estimate");
        this.itemized_total = totals.querySelector(":scope>.job-itemized");
        this.debit_total = totals.querySelector(":scope>.job-debit");
        this.debited_total = totals.querySelector(":scope>.job-debited");
        this.balance_total = totals.querySelector(":scope>.job-balance");
    }

    recalculate() {
        double estimate = 0.0;
        double itemized = 0.0;
        double debit = 0.0;
        double debited = 0.0;
        double balance = 0.0;

        var invoiced = this.querySelectorAll(":scope tr.job-row.invoiced");
        for (JobRow row in invoiced) {
            estimate += row.estimate;
            itemized += row.itemized;
            debit += row.debit_amount;
            debited += row.original_debited;
            balance += row.original_balance;
        }
        debited += debit;
        balance += debit;

        estimate_total.text = CURRENCY.format(estimate);
        itemized_total.text = CURRENCY.format(itemized);
        debit_total.text = CURRENCY.format(debit);
        debited_total.text = CURRENCY.format(debited);
        balance_total.text = CURRENCY.format(balance);
    }
}

class JobRow extends TableRowElement {

    CheckboxInputElement is_invoiced_input;
    TextInputElement flat_amount_input;
    HiddenInputElement is_flat_input;
    HiddenInputElement debit_amount_input;
    TextAreaElement debit_comment_input;

    DivElement debit_amount_div;
    TableCellElement debited_cell;
    TableCellElement balance_cell;

    double estimate;
    double itemized;
    double original_debited;
    double original_balance;

    bool get is_invoiced => is_invoiced_input.checked;

    double get debit_amount => double.parse(debit_amount_input.value);
    set debit_amount(double amount) {
        this.debit_amount_input.value = amount.toString();
        this.debit_amount_div.text = CURRENCY.format(amount);
        this.debited_cell.text = CURRENCY.format(amount+original_debited);
        this.balance_cell.text = CURRENCY.format(amount+original_balance);
        (parent.parent as JobTable).recalculate();
    }

    JobRow.created() : super.created() {
        this.is_invoiced_input = this.querySelector(":scope>.job-invoiced>input");
        this.is_invoiced_input.onChange.listen(invoicing_toggled);
        this.is_flat_input = this.querySelector(":scope>.job-flat>input[type='hidden']");
        this.flat_amount_input = this.querySelector(":scope>.job-flat>input[type='text']");
        this.flat_amount_input.onKeyUp.listen(flat_amount_changed);
        this.debit_amount_input = this.querySelector(":scope>.job-debit>input");

        this.debit_amount_div = this.querySelector(":scope>.job-debit>.job-debit-amount");
        this.debit_comment_input = this.querySelector(":scope>.job-debit>.job-debit-comment");
        this.debited_cell = this.querySelector(":scope>.job-debited");
        this.balance_cell = this.querySelector(":scope>.job-balance");

        this.estimate = double.parse(this.querySelector(":scope>.job-estimate").dataset['amount']);
        this.itemized = double.parse(this.querySelector(":scope>.job-itemized").dataset['amount']);
        this.original_debited = double.parse(debited_cell.dataset['amount']);
        this.original_balance = double.parse(balance_cell.dataset['amount']);
    }

    update_debit() {
        double debit = 0.0;
        if (this.flat_amount_input.value.length > 0) {
            double flat_amount = 0.0;
            try {
                flat_amount = parse_decimal(this.flat_amount_input.value);
            } on FormatException catch (e) {}
            if (flat_amount > this.itemized) {
                debit = flat_amount - this.original_debited;
                if (debit > 0.0) {
                    debit_amount = debit;
                    is_flat_input.value = "True";
                    classes.add('flat');
                    return;
                }
            }
        }
        if (this.itemized > this.original_debited) {
            debit = this.itemized - this.original_debited;
        }
        debit_amount = debit;
        is_flat_input.value = "False";
        classes.remove('flat');
    }

    invoicing_toggled(Event e) {
        if (is_invoiced) {
            classes.add('invoiced');
            flat_amount_input.disabled = false;
            update_debit();
        } else {
            classes.remove('invoiced');
            debit_amount = 0.0;
            flat_amount_input.disabled = true;
        }
    }

    flat_amount_changed(Event e) {
        update_debit();
    }

}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('job-table', JobTable, extendsTag:'table');
    document.registerElement('job-row', JobRow, extendsTag:'tr');


    /*
NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");
NumberFormat SPLIT = new NumberFormat("#,###,###,##0.00");

    InputElement amount_input = querySelector('input[name="amount"]');
    CheckboxInputElement is_tax_included_input = querySelector('input[name="is_tax_included"]');
    TableCellElement gross_amount = querySelector('td[id="gross-amount"]');
    TableCellElement net_amount = querySelector('td[id="net-amount"]');
    TableCellElement tax_amount = querySelector('td[id="tax-amount"]');
    double TAX_RATE = parse_decimal(tax_amount.dataset['tax-rate']);

    InputElement payment_input = querySelector('input[name="amount"]');
    payment_input.onKeyUp.listen((e) {
        double payment = parse_decimal(payment_input.value);
        var splits = querySelectorAll('[name^="split-"][name\$="-amount"]');
        int split_amount = payment / splits.length;
        splits.forEach((e) {
            e.value = SPLIT.format(split_amount);
        });
    });

    var update_table = (e) {
        // this should always match the Python implementation in apps/document/type/invoice.py
        double amount = parse_decimal(amount_input.value);
        if (is_tax_included_input.checked) {
            double net = amount / (1 + TAX_RATE);
            gross_amount.text = AMOUNT.format(amount);
            net_amount.text = AMOUNT.format(net);
            tax_amount.text = AMOUNT.format(amount-net);
        } else {
            double tax = amount * TAX_RATE;
            gross_amount.text = AMOUNT.format(amount+tax);
            net_amount.text = AMOUNT.format(amount);
            tax_amount.text = AMOUNT.format(tax);
        }
    };

    update_table(null);
    amount_input.onKeyUp.listen(update_table);
    is_tax_included_input.onChange.listen(update_table);
    */
}
