import 'dart:html';
import 'package:intl/intl.dart';
import 'package:systori/inputs.dart';


class RefundTable extends TableElement {

    AmountViewCell refund_total_cell;
    AmountViewCell credit_total_cell;
    AmountViewCell issue_refund_cell;

    double tax_rate;

    ElementList<RefundRow> get rows =>
            this.querySelectorAll(":scope tr.refund-row");

    RefundTable.created() : super.created(); attached() {
        TableRowElement totals = this.querySelector(":scope tr.refund-table-totals");
        this.refund_total_cell = totals.querySelector(":scope>.job-refund");
        this.credit_total_cell = totals.querySelector(":scope>.job-credit");
        this.issue_refund_cell = querySelector(".issue-refund");
        tax_rate = double.parse(this.dataset['tax-rate']);
    }

    recalculate() {

        Amount refund_total = new Amount.from(0, 0, tax_rate);
        for (RefundRow row in rows) {
            refund_total += row.refund_cell.amount;
        }
        refund_total_cell.update(refund_total);

        Amount credit_total = new Amount.from(0, 0, tax_rate);
        for (RefundRow row in rows) {
            refund_total = row.consume_refund(refund_total);
            credit_total += row.credit_cell.amount;
        }
        credit_total_cell.update(credit_total);
        issue_refund_cell.update(refund_total);
    }

}


class RefundRow extends TableRowElement {

    RefundTable table;

    AmountViewCell paid_cell;
    AmountViewCell invoiced_cell;
    AmountViewCell progress_cell;
    AmountInputCell refund_cell;
    AmountInputCell credit_cell;

    RefundRow.created() : super.created(); attached() {
        table = parent.parent;

        paid_cell = this.querySelector(":scope>.job-paid");
        paid_cell.onClick.listen(column_clicked);
        invoiced_cell = this.querySelector(":scope>.job-invoiced");
        progress_cell = this.querySelector(":scope>.job-progress");

        refund_cell = this.querySelector(":scope>.job-refund");
        refund_cell.onAmountChange.listen(amount_changed);
        credit_cell = this.querySelector(":scope>.job-credit");
        credit_cell.onAmountChange.listen(amount_changed);
    }

    consume_refund(Amount refund) {
        if (refund_cell.amount.gross.decimal > 0) {
            // don't apply the refunds back on the row that's being refunded
            credit_cell.zero();
            return refund;
        }
        if (progress_cell.amount.gross > paid_cell.amount.gross) {
            var consumable = progress_cell.amount - paid_cell.amount;
            if (refund.gross < consumable.gross) {
                consumable = refund;
            }
            credit_cell.update(consumable);
            refund -= consumable;
        }
        return refund;
    }

    amount_changed(AmountChangeEvent e) {
        table.recalculate();
    }

    column_clicked(MouseEvent e) {
        Amount new_refund_amount = (e.currentTarget as AmountViewCell).amount;
        refund_cell.update(new_refund_amount, triggerEvent: true);
    }
}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('refund-table', RefundTable, extendsTag:'table');
    document.registerElement('refund-row', RefundRow, extendsTag:'tr');
}
