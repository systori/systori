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
    double tax_rate;

    int get payment =>
            (parse_currency(payment_input.value) * 100).round();

    ElementList<PaymentSplit> get rows =>
            this.querySelectorAll(":scope tr.payment-split-row");

    PaymentSplitTable.created() : super.created(); attached() {
        TableRowElement totals = this.querySelector(":scope tr.split-table-totals");
        payment_gross_total = totals.querySelector(":scope>.job-payment");
        discount_gross_total = totals.querySelector(":scope>.job-discount");
        credit_gross_total = totals.querySelector(":scope>.job-credit");
        payment_input = document.querySelector('input[name="amount"]');
        payment_input.onKeyUp.listen(auto_split);
        discount_select = this.querySelector('select[name="discount"]');
        discount_select.onChange.listen(auto_split);
        discount_percent = double.parse(discount_select.value);
        tax_rate = double.parse(this.dataset['tax-rate']);
    }

    auto_split([Event e]) {
        discount_percent = double.parse(discount_select.value);
        var remaining = new Amount(0, 0, payment, tax_rate);
        for (PaymentSplit row in rows) {
            remaining = row.consume_payment(remaining);
        }
        //recalculate();
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
    AmountStatefulCell discount_cell;
    AmountViewCell credit_cell;

    PaymentSplit.created() : super.created(); attached() {
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

    Amount consume_payment(Amount payment) {

        Amount discount = balance_cell.amount * table.discount_percent;
        Amount apply = balance_cell.amount - discount;

        if (payment.gross <= 0 || apply.gross <= 0) {
            payment_cell.zero();
            discount_cell.zero();
            credit_cell.zero();
            return payment;
        }

        if (payment.gross < apply.gross) {
            discount = payment * table.discount_percent;
            apply = payment - discount;
            payment.zero();

        } else {
            // payment fully covers the balance
            // reduce payment by how much was applied here
            payment -= apply;
        }

        payment_cell.update(apply);
        discount_cell.update(discount);
        credit_cell.update(apply + discount);

        return payment;
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('payment-split-table', PaymentSplitTable, extendsTag:'table');
    document.registerElement('payment-split', PaymentSplit, extendsTag:'tr');
}
