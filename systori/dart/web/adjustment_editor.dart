import 'dart:html';
import 'package:intl/intl.dart';
import 'package:systori/inputs.dart';
import 'package:systori/numbers.dart';


class AdjustmentTable extends TableElement {

    AmountViewCell adjustment_total_cell;
    AmountViewCell corrected_total_cell;

    Amount tax_rate;

    ElementList<AdjustmentRow> get rows =>
            this.querySelectorAll(":scope tr.adjustment-row");

    AdjustmentTable.created() : super.created(); attached() {
        TableRowElement totals = this.querySelector(":scope tr.adjustment-table-totals");
        this.adjustment_total_cell = totals.querySelector(":scope>.job-adjustment");
        this.corrected_total_cell = totals.querySelector(":scope>.job-corrected");
        tax_rate = new Amount.fromStrings('0', '0', this.dataset['tax-rate']);

        querySelector('#match-overpaid')?.onClick?.listen(match_overpaid);
        querySelector('#match-underpaid')?.onClick?.listen(match_underpaid);
        querySelector('#match-overbilled')?.onClick?.listen(match_overbilled);
        querySelector('#reset-adjustments')?.onClick?.listen(reset_adjustments);
    }

    recalculate() {
        Amount adjustment_total = tax_rate.zero(),
               corrected_total = tax_rate.zero();
        for (AdjustmentRow row in rows) {
            adjustment_total += row.adjustment_cell.amount;
            corrected_total += row.corrected_cell.amount;
        }
        adjustment_total_cell.update(adjustment_total);
        corrected_total_cell.update(corrected_total);
    }

    match_overpaid(MouseEvent e) {
        for (AdjustmentRow row in rows) {
            if (row.paid_cell.amount.gross > row.invoiced_cell.amount.gross) {
                row.corrected_cell.update(row.paid_cell.amount);
                row.adjustment_cell.update(row.corrected_cell.amount - row.invoiced_cell.amount);
                row.update_selected();
            }
        }
        recalculate();
    }

    match_underpaid(MouseEvent e) {
        for (AdjustmentRow row in rows) {
            if (row.paid_cell.amount.gross < row.invoiced_cell.amount.gross) {
                row.corrected_cell.update(row.paid_cell.amount);
                row.adjustment_cell.update(row.corrected_cell.amount - row.invoiced_cell.amount);
                row.update_selected();
            }
        }
        recalculate();
    }

    match_overbilled(MouseEvent e) {
        for (AdjustmentRow row in rows) {
            if (row.invoiced_cell.amount.gross > row.progress_cell.amount.gross) {
                row.corrected_cell.update(row.progress_cell.amount);
                row.adjustment_cell.update(row.corrected_cell.amount - row.invoiced_cell.amount);
                row.update_selected();
            }
        }
        recalculate();
    }

    reset_adjustments(MouseEvent e) {
        for (AdjustmentRow row in rows) {
            if (row.invoiced_cell.amount != row.corrected_cell.amount) {
                row.corrected_cell.update(row.invoiced_cell.amount);
                row.adjustment_cell.update(row.corrected_cell.amount - row.invoiced_cell.amount);
                row.update_selected();
            }
        }
        recalculate();
    }

}


class AdjustmentRow extends TableRowElement {

    AdjustmentTable table;

    AmountViewCell paid_cell;
    AmountViewCell invoiced_cell;
    AmountViewCell progress_cell;
    AmountInputCell adjustment_cell;
    AmountInputCell corrected_cell;

    AdjustmentRow.created() : super.created(); attached() {
        table = parent.parent;

        paid_cell = this.querySelector(":scope>.job-paid");
        paid_cell?.onClick?.listen((e)=>column_clicked(paid_cell));
        invoiced_cell = this.querySelector(":scope>.job-invoiced");
        invoiced_cell.onClick.listen((e)=>column_clicked(invoiced_cell));
        progress_cell = this.querySelector(":scope>.job-progress");
        progress_cell?.onClick?.listen((e)=>column_clicked(progress_cell));

        adjustment_cell = this.querySelector(":scope>.job-adjustment");
        adjustment_cell.onAmountChange.listen(adjustment_changed);
        corrected_cell = this.querySelector(":scope>.job-corrected");
        corrected_cell.onAmountChange.listen(corrected_changed);
    }

    adjustment_changed(AmountChangeEvent e) {
        corrected_cell.update(invoiced_cell.amount + adjustment_cell.amount);
        update_selected();
        table.recalculate();
    }

    corrected_changed(AmountChangeEvent e) {
        adjustment_cell.update(corrected_cell.amount - invoiced_cell.amount);
        update_selected();
        table.recalculate();
    }

    column_clicked(AmountViewCell cell) =>
        corrected_cell.update(cell.amount, triggerEvent: true);

    update_selected() {
        for (AmountCell cell in [paid_cell, invoiced_cell, progress_cell]) {
            if (cell == null) continue;
            cell.classes.remove('selected');
            if (cell.amount == corrected_cell.amount) {
                cell.classes.add('selected');
            }
        }
    }
}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('adjustment-table', AdjustmentTable, extendsTag:'table');
    document.registerElement('adjustment-row', AdjustmentRow, extendsTag:'tr');
}
