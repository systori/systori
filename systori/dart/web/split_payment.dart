import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';
import 'amount_element.dart';


class PaymentSplitTable extends TableElement {

    TextInputElement payment_input;
    SelectElement discount_select;

    TableCellElement payment_gross_total;
    TableCellElement discount_gross_total;
    TableCellElement credit_gross_total;

    double discount_percent;

    PaymentSplitTable.created() : super.created() {
        TableRowElement totals = this.querySelector(":scope tr.split-table-totals");
        this.payment_gross_total = totals.querySelector(":scope>.job-payment");
        this.discount_gross_total = totals.querySelector(":scope>.job-discount");
        this.credit_gross_total = totals.querySelector(":scope>.job-credit");
        payment_input = document.querySelector('input[name="amount"]');
        payment_input.onKeyUp.listen(update_table);
        discount_select = this.querySelector('select[name="discount"]');
        discount_select.onChange.listen(update_table);
        discount_percent = double.parse(discount_select.value);
    }

    update_table(Event e) {
        discount_percent = double.parse(discount_select.value);
        int remaining = (parse_currency(payment_input.value) * 100).round();
        var rows = this.querySelectorAll(":scope tr.payment-split-row");
        for (PaymentSplit row in rows) {
            remaining = row.consume_payment(remaining);
        }
        recalculate();
    }

    recalculate() {

        int payment_gross = 0,
            discount_gross = 0,
            credit_gross = 0;

        var rows = this.querySelectorAll(":scope tr.payment-split-row");
        for (PaymentSplit row in rows) {
            payment_gross += row.payment_cell.gross;
            discount_gross += row.discount_cell.gross;
            credit_gross += row.credit_cell.gross;
        }

        payment_gross_total.text = AMOUNT.format(payment_gross/100);
        discount_gross_total.text = AMOUNT.format(discount_gross/100);
        credit_gross_total.text = AMOUNT.format(credit_gross/100);
    }

}

class PaymentSplit extends TableRowElement {

    PaymentSplitTable table;

    AmountViewCell balance_cell;
    AmountInputCell payment_cell;
    AmountViewInputCell discount_cell;
    AmountViewCell credit_cell;

    PaymentSplit.created() : super.created() {
        table = parent.parent;
        balance_cell = this.querySelector(":scope>.job-balance");
        payment_cell = this.querySelector(":scope>.job-payment");
        payment_cell.onAmountChange.listen(input_changed);
        discount_cell = this.querySelector(":scope>.job-discount");
        credit_cell = this.querySelector(":scope>.job-credit");
    }

    input_changed([Event e]) {
        int payment_gross = payment_cell.gross;
        int full_amount = (payment_gross/(1-table.discount_percent)).round();
        int discount_gross = full_amount - payment_gross;
        int _tax = (discount_gross / payment_cell.inverse_tax_rate).round();
        discount_cell.tax = _tax;
        discount_cell.gross = discount_gross;
        discount_input_net.value = ((discount_gross-_tax)/100).toStringAsFixed(2);
        discount_span.text = AMOUNT.format(discount_gross/100);

        credit_gross = payment_gross + discount_gross;
        credit_cell.text = AMOUNT.format(credit_gross/100);

        if (e != null) table.recalculate();
    }

    int consume_payment(int payment) {

        int discount_gross = (balance_cell.gross * table.discount_percent).round();
        int discount_net = (balance_cell.net * table.discount_percent).round();
        int discount_tax = discount_gross - discount_net;

        int apply_gross = balance_cell.gross - discount_gross;
        int apply_net = balance_cell.net - discount_net;
        int apply_tax = apply_gross - apply_net;

        if (payment <= 0 || apply_gross <= 0) {
            payment_cell.zero();
            discount_cell.zero();
            credit_cell.zero();
            return payment;
        }

        if (payment < apply_gross) {
            // payment is less than amount due, we're going to use all of it up
            // since payment < balance, we need to recalculate everything

            // TODO: refactor this
            int payment_tax = (payment / (1.0 + (1.0 / 0.19))).round();
            int payment_net = payment - payment_tax;

            discount_gross = (payment * table.discount_percent).round();
            discount_net = (payment_net * table.discount_percent).round();
            discount_tax = discount_gross - discount_net;

            apply_gross = payment - discount_gross;
            apply_net = payment_net - discount_net;
            apply_tax = apply_gross - apply_net;

            payment = 0;

        } else {
            // payment fully covers the balance
            // reduce payment by how much was applied here
            payment -= apply_gross;
        }

        payment_cell.gross = apply_gross;
        payment_cell.net = apply_net;
        payment_cell.tax = apply_tax;

        discount_cell.gross = discount_gross;
        discount_cell.net = discount_net;
        discount_cell.tax = discount_tax;

        credit_cell.gross = apply_gross + discount_gross;
        credit_cell.net = apply_net + discount_net;
        credit_cell.tax = apply_tax + discount_tax;

        return payment;
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('payment-split-table', PaymentSplitTable, extendsTag:'table');
    document.registerElement('payment-split', PaymentSplit, extendsTag:'tr');
}
