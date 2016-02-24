import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");

int amount_string_to_int(amount) {
    return (double.parse(amount) * 100).round();
}


class AdjustmentTable extends TableElement {

    TableCellElement correction_total_cell;
    TableCellElement adjustment_total_cell;

    AdjustmentTable.created() : super.created() {
        TableRowElement totals = this.querySelector(":scope tr.adjustment-table-totals");
        this.correction_total_cell = totals.querySelector(":scope>.job-correction");
        this.adjustment_total_cell = totals.querySelector(":scope>.job-adjustment");
    }

    recalculate() {
        int correction_total = 0;
        int adjustment_total = 0;
        var rows = this.querySelectorAll(":scope tr.adjustment-row");
        for (AdjustmentRow row in rows) {
            correction_total += row.correction;
            adjustment_total += row.adjustment;
        }
        correction_total_cell.text = AMOUNT.format(correction_total/100);
        adjustment_total_cell.text = AMOUNT.format(adjustment_total/100);
    }

}


class AdjustmentRow extends TableRowElement {

    TextInputElement correction_input;
    TextInputElement adjustment_input;

    // 1.00 -> 100
    int invoiced;
    int correction;
    int adjustment;

    AdjustmentRow.created() : super.created() {
        TableCellElement invoiced_cell = this.querySelector(":scope>.job-invoiced");
        this.invoiced = amount_string_to_int(invoiced_cell.dataset['amount']);

        this.correction_input = this.querySelector('input[name\$="-correction"]');
        this.correction_input.onKeyUp.listen(correction_changed);
        this.correction = (parse_currency(correction_input.value) * 100).round();

        this.adjustment_input = this.querySelector('input[name\$="-adjustment"]');
        this.adjustment_input.onKeyUp.listen(adjustment_changed);
        this.adjustment = (parse_currency(adjustment_input.value) * 100).round();

    }

    correction_changed([Event e]) {
        this.correction = (parse_currency(correction_input.value) * 100).round();
        this.adjustment = this.invoiced - this.correction;
        this.adjustment_input.value = AMOUNT.format(this.adjustment/100);
        (parent.parent as AdjustmentTable).recalculate();
    }

    adjustment_changed([Event e]) {
        this.adjustment = (parse_currency(adjustment_input.value) * 100).round();
        this.correction = this.invoiced - this.adjustment;
        this.correction_input.value = AMOUNT.format(this.correction/100);
        (parent.parent as AdjustmentTable).recalculate();
    }

}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('adjustment-table', AdjustmentTable, extendsTag:'table');
    document.registerElement('adjustment-row', AdjustmentRow, extendsTag:'tr');
}
