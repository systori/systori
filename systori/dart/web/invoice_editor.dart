import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");


class InvoiceTable extends TableElement {
    TableCellElement debit_net_total;

    InvoiceTable.created() : super.created() {
        TableRowElement totals = this.querySelector(":scope tr.job-table-totals");
        this.debit_net_total = totals.querySelector(":scope>.job-amount-net");
    }

    recalculate() {
        double debit_net = 0.0;
        var invoiced = this.querySelectorAll(":scope tr.job-row.invoiced");
        for (InvoiceDebit row in invoiced) {
            debit_net += row.net_amount;
        }
        debit_net_total.text = AMOUNT.format(debit_net);
    }
}

class InvoiceDebit extends TableRowElement {

    CheckboxInputElement is_invoiced_input;
    RangeInputElement flat_invoice_range_input;
    TextInputElement net_amount_input;
    HiddenInputElement is_override_input;
    TextAreaElement override_comment_input;

    TableCellElement net_estimate_cell;
    TableCellElement net_invoiced_cell;
    AnchorElement net_itemized_anchor;

    double net_estimate;
    double net_invoiced;
    double net_itemized;
    double net_amount;

    bool get is_invoiced => is_invoiced_input.checked;

    InvoiceDebit.created() : super.created() {
        this.is_invoiced_input = this.querySelector('[name^="job-"][name\$="-is_invoiced"]');
        this.is_invoiced_input.onChange.listen(invoicing_toggled);

        this.net_estimate_cell = this.querySelector(":scope>.job-estimated");
        this.net_estimate = double.parse(net_estimate_cell.dataset['amount']);
        this.net_invoiced_cell = this.querySelector(":scope>.job-debited");
        this.net_invoiced = double.parse(net_invoiced_cell.dataset['amount']);

        this.flat_invoice_range_input = this.querySelector('[type="range"]');
        this.flat_invoice_range_input.onInput.listen(flat_invoice_range_changed);
        this.querySelectorAll('.percent-button').onClick.listen(flat_invoice_percent_clicked);

        this.net_itemized_anchor = this.querySelector(":scope>.job-itemized>a");
        this.net_itemized_anchor.onClick.listen(itemized_value_clicked);
        this.net_itemized = double.parse(net_itemized_anchor.dataset['amount']);

        this.net_amount_input = this.querySelector('[name^="job-"][name\$="-amount_net"]');
        this.net_amount_input.onKeyUp.listen(net_amount_changed);
        this.net_amount = parse_currency(net_amount_input.value);
        this.is_override_input = this.querySelector('[name^="job-"][name\$="-is_override"]');
        this.override_comment_input = this.querySelector('[name^="job-"][name\$="-override_comment"]');
    }

    invoicing_toggled([Event e]) {
        if (is_invoiced) {
            classes.add('invoiced');
            net_amount_input.disabled = false;
            flat_invoice_range_input.disabled = false;
            net_itemized_anchor.classes.remove('disabled');
            this.querySelectorAll('.percent-button').forEach((e) {
                e.classes.remove('disabled');
            });
        } else {
            classes.remove('invoiced');
            net_amount_input.disabled = true;
            flat_invoice_range_input.disabled = true;
            net_itemized_anchor.classes.add('disabled');
            this.querySelectorAll('.percent-button').forEach((e) {
               e.classes.add('disabled');
            });
        }
    }

    flat_invoice_range_changed(Event e) {
        double percent = int.parse(flat_invoice_range_input.value)/100;
        double flat = net_estimate * percent - net_invoiced;
        update_net_amount(flat < 0 ? 0 : flat);
    }

    flat_invoice_percent_clicked(Event e) {
        double percent = double.parse((e.target as AnchorElement).dataset['percent'])/100;
        double flat = net_estimate * percent - net_invoiced;
        update_net_amount(flat < 0 ? 0 : flat);
        update_range_slider();
    }

    itemized_value_clicked(Event e) {
        update_net_amount(net_itemized);
        update_range_slider();
    }

    net_amount_changed(Event e) {
        update_net_amount();
        update_range_slider();
    }

    update_range_slider() {
        var invoiced_total = net_invoiced + net_amount;
        if (invoiced_total > net_estimate) {
            flat_invoice_range_input.value = '100';
        } else {
            flat_invoice_range_input.value = (invoiced_total / net_estimate * 100).round().toString();
        }
    }

    update_net_amount([double amount]) {
        if (amount != null) {
            net_amount = amount;
            net_amount_input.value = AMOUNT.format(amount);
        } else {
            net_amount = parse_currency(net_amount_input.value);
        }
        is_override_input.value = 'False';
        classes.remove('override');
        classes.remove('itemized');
        if (net_amount > 0) {
            if (net_amount == net_itemized) {
                is_override_input.value = 'False';
                classes.add('itemized');
            } else {
                is_override_input.value = 'True';
                classes.add('override');
            }
        }
        (parent.parent as InvoiceTable).recalculate();
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
