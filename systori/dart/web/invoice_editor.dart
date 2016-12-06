import 'dart:html';
import 'package:intl/intl.dart';
import 'package:systori/inputs.dart';
import 'package:systori/decimal.dart';


class InvoiceTable extends TableElement {

    AmountViewCell estimate_total_cell;
    AmountViewCell progress_total_cell;
    AmountViewCell invoiced_total_cell;
    AmountViewCell itemized_total_cell;
    AmountViewCell debit_total_cell;

    double tax_rate;

    ElementList<InvoiceRow> get rows =>
            this.querySelectorAll(":scope tr[is=invoice-row].invoiced");

    InvoiceTable.created() : super.created(); attached() {
        TableRowElement totals = this.querySelector(":scope tr.invoice-table-totals");
        this.estimate_total_cell = totals.querySelector(":scope>.job-estimate");
        this.progress_total_cell = totals.querySelector(":scope>.job-progress");
        this.invoiced_total_cell = totals.querySelector(":scope>.job-invoiced");
        this.itemized_total_cell = totals.querySelector(":scope>.job-itemized");
        this.debit_total_cell = totals.querySelector(":scope>.job-debit");
        tax_rate = double.parse(this.dataset['tax-rate']);
    }

    recalculate() {

        var estimate_total = new Amount.from(0, 0, tax_rate),
            progress_total = new Amount.from(0, 0, tax_rate),
            invoiced_total = new Amount.from(0, 0, tax_rate),
            itemized_total = new Amount.from(0, 0, tax_rate),
            debit_total = new Amount.from(0, 0, tax_rate);

        for (var row in rows) {
            estimate_total += row.estimate_cell.amount;
            progress_total += row.progress_cell.amount;
            invoiced_total += row.invoiced_cell.amount;
            itemized_total += row.itemized_cell.amount;
            debit_total += row.debit_cell.amount;
        }

        estimate_total_cell.update(estimate_total);

        progress_total_cell.update(progress_total);
        progress_total_cell.updatePercent(
                estimate_total.net.decimal > 0 ? (progress_total.net/estimate_total.net).decimal * 100 : 0.0);

        invoiced_total_cell.update(invoiced_total);
        invoiced_total_cell.updatePercent(
                progress_total.net.decimal > 0 ? (invoiced_total.net/progress_total.net).decimal * 100 : 0.0);

        itemized_total_cell.update(itemized_total);

        debit_total_cell.update(debit_total);
    }
}


class InvoiceRow extends TableRowElement {

    InvoiceTable table;

    CheckboxInputElement is_invoiced_input;
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

        is_override_input = this.querySelector('[name^="job-"][name\$="-is_override"]');
        override_comment_input = this.querySelector('[name^="job-"][name\$="-override_comment"]');
    }

    invoicing_toggled([Event e]) {
        is_invoiced ? classes.add('invoiced') : classes.remove('invoiced');
        _clear_django_errors();
        table.recalculate();
    }

    itemized_amount_clicked(Event e) {
        debit_cell.update(itemized_cell.amount);
        debit_amount_updated();
    }

    debit_amount_updated([AmountChangeEvent e]) {

        // invoice shows job as itemized only when invoiced == progress
        if (invoiced_cell.amount + debit_cell.amount == progress_cell.amount) {
            classes.add('itemized');
        } else {
            classes.remove('itemized');
        }

        // itemized cell is highlighted if it matches the debit
        if (itemized_cell.amount == debit_cell.amount) {
            itemized_cell.classes.add('selected');
        } else {
            itemized_cell.classes.remove('selected');
        }

        if (itemized_cell.amount != debit_cell.amount && debit_cell.amount.gross.decimal > 0) {
            is_override_input.value = 'True';
            classes.add('override');
        } else {
            is_override_input.value = 'False';
            classes.remove('override');
        }

        _clear_django_errors();

        table.recalculate();
    }

    _clear_django_errors() {
        debit_cell.classes.removeAll(['has-error', 'bg-danger']);
        debit_cell.querySelector('p.comment-error')?.remove();
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('invoice-table', InvoiceTable, extendsTag:'table');
    document.registerElement('invoice-row', InvoiceRow, extendsTag:'tr');
}
