import 'dart:html';
import 'package:intl/intl.dart';
import 'amount_element.dart';


class InvoiceTable extends TableElement {

    AmountViewCell debit_total_cell;

    double tax_rate;

    ElementList<InvoiceRow> get rows =>
            this.querySelectorAll(":scope tr.invoice-row.invoiced");

    InvoiceTable.created() : super.created(); attached() {
        TableRowElement totals = this.querySelector(":scope tr.invoice-table-totals");
        this.debit_total_cell = totals.querySelector(":scope>.job-debit");
        tax_rate = double.parse(this.dataset['tax-rate']);
    }

    recalculate() {
        var debit_total = new Amount(0, 0, tax_rate);
        for (var row in rows) {
            debit_total += row.debit_cell.amount;
        }
        debit_total_cell.update(debit_total);
    }
}


class InvoiceRow extends TableRowElement {

    InvoiceTable table;

    CheckboxInputElement is_invoiced_input;
    RangeInputElement flat_invoice_range_input;
    HiddenInputElement is_override_input;
    TextAreaElement override_comment_input;

    AmountViewCell estimate_cell;
    AmountViewCell progress_cell;
    AmountViewCell invoiced_cell;
    AmountViewCell itemized_cell;

    AmountInputCell debit_cell;

    bool get is_invoiced => is_invoiced_input.checked;

    InvoiceRow.created() : super.created(); attached() {

        table = parent.parent;

        is_invoiced_input = this.querySelector(':scope>.job-is-invoiced>input');
        is_invoiced_input.onChange.listen(invoicing_toggled);

        estimate_cell = this.querySelector(":scope>.job-estimate");
        progress_cell = this.querySelector(":scope>.job-progress");
        invoiced_cell = this.querySelector(":scope>.job-invoiced");
        itemized_cell = this.querySelector(":scope>.job-itemized");
        itemized_cell.onClick.listen(itemized_amount_clicked);

        debit_cell = this.querySelector(":scope>.job-debit");
        debit_cell.onAmountChange.listen(debit_amount_updated);

        this.flat_invoice_range_input = this.querySelector('[type="range"]');
        this.flat_invoice_range_input.onInput.listen(flat_invoice_range_changed);
        this.querySelectorAll('.percent-button').onClick.listen(flat_invoice_percent_clicked);

        this.is_override_input = this.querySelector('[name^="job-"][name\$="-is_override"]');
        this.override_comment_input = this.querySelector('[name^="job-"][name\$="-override_comment"]');
    }

    invoicing_toggled([Event e]) {
        if (is_invoiced) {
            classes.add('invoiced');
            flat_invoice_range_input.disabled = false;
            this.querySelectorAll('.percent-button').forEach((e) {
                e.classes.remove('disabled');
            });
        } else {
            classes.remove('invoiced');
            flat_invoice_range_input.disabled = true;
            this.querySelectorAll('.percent-button').forEach((e) {
               e.classes.add('disabled');
            });
        }
        table.recalculate();
    }

    itemized_amount_clicked(Event e) {
        debit_cell.update(itemized_cell.amount);
        update_range_slider();
        debit_amount_updated();
    }

    flat_invoice_range_changed(Event e) {
        double percent = int.parse(flat_invoice_range_input.value)/100;
        Amount flat = estimate_cell.amount * percent - invoiced_cell.amount;
        debit_cell.update(flat.gross < 0 ? new Amount.zeroed() : flat);
        debit_amount_updated();
    }

    flat_invoice_percent_clicked(Event e) {
        double percent = double.parse((e.target as AnchorElement).dataset['percent'])/100;
        Amount flat = estimate_cell.amount * percent - invoiced_cell.amount;
        debit_cell.update(flat.gross < 0 ? new Amount.zeroed() : flat);
        update_range_slider();
        debit_amount_updated();
    }

    update_range_slider() {
        var invoiced_total = invoiced_cell.amount + debit_cell.amount;
        if (invoiced_total.gross > estimate_cell.amount.gross) {
            flat_invoice_range_input.value = '100';
        } else {
            flat_invoice_range_input.value = (invoiced_total.gross / estimate_cell.amount.gross * 100).round().toString();
        }
    }

    debit_amount_updated([AmountChangeEvent e]) {
        is_override_input.value = 'False';
        classes.remove('override');
        classes.remove('itemized');
        var debit_gross = debit_cell.amount.gross;
        if (debit_gross > 0) {
            if (debit_gross == itemized_cell.amount.gross) {
                is_override_input.value = 'False';
                classes.add('itemized');
            } else {
                is_override_input.value = 'True';
                classes.add('override');
            }
        }
        table.recalculate();
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('invoice-table', InvoiceTable, extendsTag:'table');
    document.registerElement('invoice-row', InvoiceRow, extendsTag:'tr');
}
