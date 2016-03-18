import 'dart:html';
import 'package:intl/intl.dart';
import 'amount_element.dart';


class AdjustmentTable extends TableElement {

    AmountViewCell approved_total_cell;
    AmountViewCell adjustment_total_cell;

    double tax_rate;

    ElementList<AdjustmentRow> get rows =>
            this.querySelectorAll(":scope tr.adjustment-row");

    AdjustmentTable.created() : super.created(); attached() {
        TableRowElement totals = this.querySelector(":scope tr.adjustment-table-totals");
        this.approved_total_cell = totals.querySelector(":scope>.job-approved");
        this.adjustment_total_cell = totals.querySelector(":scope>.job-adjustment");
        tax_rate = double.parse(this.dataset['tax-rate']);
    }

    recalculate() {
        Amount approved_total = new Amount(0, 0, tax_rate),
               adjustment_total = new Amount(0, 0, tax_rate);
        for (AdjustmentRow row in rows) {
            approved_total += row.approved_cell.amount;
            adjustment_total += row.adjustment_cell.amount;
        }
        approved_total_cell.update(approved_total);
        adjustment_total_cell.update(adjustment_total);
    }

}


class AdjustmentRow extends TableRowElement {

    AdjustmentTable table;

    AmountViewCell invoiced_cell;
    AmountInputCell approved_cell;
    AmountInputCell adjustment_cell;

    AdjustmentRow.created() : super.created(); attached() {
        table = parent.parent;
        invoiced_cell = this.querySelector(":scope>.job-invoiced");
        approved_cell = this.querySelector(":scope>.job-approved");
        approved_cell.onAmountChange.listen(approved_changed);
        adjustment_cell = this.querySelector(":scope>.job-adjustment");
        adjustment_cell.onAmountChange.listen(adjustment_changed);
    }

    approved_changed(AmountChangeEvent e) {
        var adjustment = invoiced_cell.amount - approved_cell.amount;
        adjustment.zero_negatives();
        adjustment_cell.update(adjustment);
        table.recalculate();
    }

    adjustment_changed(AmountChangeEvent e) {
        var approved = invoiced_cell.amount - adjustment_cell.amount;
        approved_cell.update(approved);
        table.recalculate();
    }

}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('adjustment-table', AdjustmentTable, extendsTag:'table');
    document.registerElement('adjustment-row', AdjustmentRow, extendsTag:'tr');
}
