import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");


class InvoiceTable extends TableElement {
    TableCellElement debit_net_total;
    TableCellElement debit_gross_total;
    TableCellElement debited_gross_total;
    TableCellElement balance_gross_total;

    InvoiceTable.created() : super.created() {
        TableRowElement totals = this.querySelector(":scope tr.job-table-totals");
        this.debit_net_total = totals.querySelector(":scope>.job-amount-net");
        this.debit_gross_total = totals.querySelector(":scope>.job-amount-gross");
        this.debited_gross_total = totals.querySelector(":scope>.job-debited");
        this.balance_gross_total = totals.querySelector(":scope>.job-balance");
    }

    recalculate() {
        double debit_net = 0.0;
        double debit_gross = 0.0;
        double debited = 0.0;
        double balance = 0.0;
        var invoiced = this.querySelectorAll(":scope tr.job-row.invoiced");
        for (InvoiceDebit row in invoiced) {
            debit_net += row.net_amount;
            debit_gross += row.gross_amount;
            debited += row.new_gross_debited;
            balance += row.new_gross_balance;
        }
        debit_net_total.text = AMOUNT.format(debit_net);
        debit_gross_total.text = AMOUNT.format(debit_gross);
        debited_gross_total.text = AMOUNT.format(debited);
        balance_gross_total.text = AMOUNT.format(balance);
    }
}

class InvoiceDebit extends TableRowElement {

    CheckboxInputElement is_invoiced_input;
    RangeInputElement flat_invoice_range_input;
    TextInputElement net_amount_input;
    HiddenInputElement is_override_input;
    TextAreaElement override_comment_input;

    TableCellElement net_estimate_cell;
    TableCellElement net_billable_cell;
    TableCellElement gross_amount_cell;
    TableCellElement gross_debited_cell;
    TableCellElement gross_balance_cell;

    double net_amount;
    double gross_amount;
    double net_estimate;
    double net_billable;
    double new_gross_debited;
    double new_gross_balance;
    double base_gross_debited;
    double base_gross_balance;

    bool get is_invoiced => is_invoiced_input.checked;

    InvoiceDebit.created() : super.created() {
        this.is_invoiced_input = this.querySelector('[name^="job-"][name\$="-is_invoiced"]');
        this.is_invoiced_input.onChange.listen(invoicing_toggled);
        this.flat_invoice_range_input = this.querySelector('[type="range"]');
        this.flat_invoice_range_input.onInput.listen(flat_invoice_range_changed);
        this.net_amount_input = this.querySelector('[name^="job-"][name\$="-amount_net"]');
        this.net_amount_input.onKeyUp.listen(net_amount_changed);
        this.is_override_input = this.querySelector('[name^="job-"][name\$="-is_override"]');
        this.override_comment_input = this.querySelector('[name^="job-"][name\$="-override_comment"]');

        this.net_billable_cell = this.querySelector(":scope>.job-billable");
        this.net_estimate_cell = this.querySelector(":scope>.job-estimated");
        this.gross_amount_cell = this.querySelector(":scope>.job-amount-gross");
        this.gross_debited_cell = this.querySelector(":scope>.job-debited");
        this.gross_balance_cell = this.querySelector(":scope>.job-balance");

        this.net_amount = double.parse(net_amount_input.value);
        this.gross_amount = double.parse(gross_amount_cell.dataset['amount']);
        this.net_billable = double.parse(net_billable_cell.dataset['amount']);
        this.net_estimate = double.parse(net_estimate_cell.dataset['amount']);
        this.new_gross_debited = double.parse(gross_debited_cell.dataset['new']);
        this.new_gross_balance = double.parse(gross_balance_cell.dataset['new']);
        this.base_gross_debited = double.parse(gross_debited_cell.dataset['base']);
        this.base_gross_balance = double.parse(gross_balance_cell.dataset['base']);
    }

    invoicing_toggled(Event e) {
        if (is_invoiced) {
            classes.add('invoiced');
            net_amount_input.disabled = false;
            update_debit();
        } else {
            classes.remove('invoiced');
            net_amount_input.disabled = true;
        }
    }

    flat_invoice_range_changed(Event e) {
        double percent = int.parse(flat_invoice_range_input.value)/100;
        net_amount_input.value = AMOUNT.format(net_estimate * percent);
        net_amount_changed(null);
        classes.add('override');
    }

    net_amount_changed([_]) {

        net_amount = parse_currency(net_amount_input.value);
        gross_amount = net_amount * 1.19;

        gross_amount_cell.text = AMOUNT.format(gross_amount);
        new_gross_debited = base_gross_debited+gross_amount;
        gross_debited_cell.text = AMOUNT.format(new_gross_debited);
        new_gross_balance = base_gross_balance+gross_amount;
        gross_balance_cell.text = AMOUNT.format(new_gross_balance);

        (parent.parent as InvoiceTable).recalculate();

        /*
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
        */
    }

}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('invoice-table', InvoiceTable, extendsTag:'table');
    document.registerElement('invoice-debit', InvoiceDebit, extendsTag:'tr');


    /*
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
