import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");


class JobsTable extends TableElement {

    TableCellElement amount_total_cell;

    // 1.00 -> 100
    int amount_total = 0;

    JobsTable.created() : super.created() {
        TableRowElement totals = this.querySelector(":scope tr.job-table-totals");
        this.amount_total_cell = totals.querySelector(":scope>.job-amount");
        this.amount_total = (parse_currency(amount_total_cell.text) * 100).round();
    }

    recalculate() {
        amount_total = 0;
        var rows = this.querySelectorAll(":scope tr.job-row");
        for (JobRow row in rows) {
            amount_total += row.amount;
        }
        amount_total_cell.text = AMOUNT.format(amount_total/100);
    }

}


class RefundTable extends JobsTable {

    DivElement refund_amount_div;

    RefundTable.created() : super.created() {
        refund_amount_div = document.querySelector('div.refund-amount');
    }

    recalculate() {
        super.recalculate();
        update_refund_amount();
    }

    update_refund_amount() {
        ApplyTable apply_table = document.querySelector('table[is="apply-table"');
        int refund = apply_table != null ? amount_total - apply_table.amount_total : amount_total;
        refund_amount_div.text = AMOUNT.format(refund/100);
    }

}


class ApplyTable extends JobsTable {

    ApplyTable.created() : super.created();

    recalculate() {
        super.recalculate();
        RefundTable refund_table = document.querySelector('table[is="refund-table"');
        refund_table.update_refund_amount();
    }

}


class JobRow extends TableRowElement {

    AnchorElement paid_anchor;
    AnchorElement overpaid_anchor;
    TextInputElement amount_input;

    // 1.00 -> 100
    int amount;

    JobRow.created() : super.created() {
        this.amount_input = this.querySelector('input[name\$="-amount"]');
        this.amount_input.onKeyUp.listen(input_changed);
        this.amount = (parse_currency(amount_input.value) * 100).round();

        this.paid_anchor = this.querySelector(":scope>.job-paid>a");
        if (this.paid_anchor != null) this.paid_anchor.onClick.listen(amount_clicked);
        this.overpaid_anchor = this.querySelector(":scope>.job-overpaid>a");
        if (this.overpaid_anchor != null) this.overpaid_anchor.onClick.listen(amount_clicked);
    }

    input_changed([Event e]) {
        this.amount = (parse_currency(amount_input.value) * 100).round();
        (parent.parent as JobsTable).recalculate();
    }

    amount_clicked(Event e) {
        amount_input.value = (e.target as AnchorElement).text;
        input_changed();
    }

}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('refund-table', RefundTable, extendsTag:'table');
    document.registerElement('apply-table', ApplyTable, extendsTag:'table');
    document.registerElement('job-row', JobRow, extendsTag:'tr');
}
