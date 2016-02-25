import 'dart:html';
import 'dart:math';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");

int amount_string_to_int(amount) {
    return (double.parse(amount) * 100).round();
}


class AdjustmentTable extends TableElement {

    TableCellElement approved_total_cell;
    TableCellElement adjustment_total_cell;
    TableCellElement adjustment_gross_total_cell;

    AdjustmentTable.created() : super.created() {
        TableRowElement totals = this.querySelector(":scope tr.adjustment-table-totals");
        this.approved_total_cell = totals.querySelector(":scope>.job-approved");
        this.adjustment_total_cell = totals.querySelector(":scope>.job-adjustment");
        this.adjustment_gross_total_cell = totals.querySelector(":scope>.job-adjustment-gross");
    }

    recalculate() {
        int approved_total = 0;
        int adjustment_total = 0;
        int adjustment_gross_total = 0;
        var rows = this.querySelectorAll(":scope tr.adjustment-row");
        for (AdjustmentRow row in rows) {
            approved_total += row.approved;
            adjustment_total += row.adjustment;
            adjustment_gross_total += row.adjustment_gross;
        }
        approved_total_cell.text = AMOUNT.format(approved_total/100);
        adjustment_total_cell.text = AMOUNT.format(adjustment_total/100);
        adjustment_gross_total_cell.text = AMOUNT.format(adjustment_gross_total/100);
    }

}


class AdjustmentRow extends TableRowElement {

    TextInputElement approved_input;
    TextInputElement adjustment_input;
    SpanElement adjustment_gross_span;
    HiddenInputElement adjustment_gross_input;

    // 1.00 -> 100
    int invoiced;
    int billable;
    int approved;
    int adjustment;
    int adjustment_gross;

    AdjustmentRow.created() : super.created() {
        TableCellElement invoiced_cell = this.querySelector(":scope>.job-invoiced");
        this.invoiced = amount_string_to_int(invoiced_cell.dataset['amount']);
        TableCellElement billable_cell = this.querySelector(":scope>.job-billable");
        this.billable = amount_string_to_int(billable_cell.dataset['amount']);

        this.approved_input = this.querySelector('input[name\$="-approved"]');
        this.approved_input.onKeyUp.listen(approved_changed);
        this.approved = (parse_currency(approved_input.value) * 100).round();

        this.adjustment_input = this.querySelector('input[name\$="-adjustment"]');
        this.adjustment_input.onKeyUp.listen(adjustment_changed);
        this.adjustment = (parse_currency(adjustment_input.value) * 100).round();

        this.adjustment_gross_input = this.querySelector('input[name\$="-adjustment_gross"]');
        this.adjustment_gross_span = this.querySelector(':scope>.job-adjustment-gross>span');
        this.adjustment_gross = amount_string_to_int(adjustment_gross_input.value);
    }

    approved_changed([Event e]) {
        this.approved = (parse_currency(approved_input.value) * 100).round();
        int approved_adjustment = this.invoiced - this.approved;
        int billable_adjustment = this.invoiced - this.billable;
        this.adjustment = max(approved_adjustment, billable_adjustment);
        this.adjustment_input.value = AMOUNT.format(this.adjustment/100);
        this.update_adjustment_gross();
        (parent.parent as AdjustmentTable).recalculate();
    }

    adjustment_changed([Event e]) {
        this.adjustment = (parse_currency(adjustment_input.value) * 100).round();
        this.update_adjustment_gross();
        (parent.parent as AdjustmentTable).recalculate();
    }

    update_adjustment_gross() {
        if (this.adjustment > this.invoiced) {
            this.adjustment = 0;
        }
        this.adjustment_gross = (this.adjustment * 1.19).round();
        this.adjustment_gross_span.text = AMOUNT.format(this.adjustment_gross/100);
        this.adjustment_gross_input.value = (this.adjustment_gross/100).toString();
    }

}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('adjustment-table', AdjustmentTable, extendsTag:'table');
    document.registerElement('adjustment-row', AdjustmentRow, extendsTag:'tr');
}
