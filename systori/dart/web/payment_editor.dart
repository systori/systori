import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';
import 'amount_element.dart';


class PaymentSplitTable extends TableElement {

    TextInputElement payment_input;
    SelectElement discount_select;

    AmountViewCell split_gross_total;
    AmountViewCell discount_gross_total;
    AmountViewCell credit_gross_total;

    double discount_percent;
    double tax_rate;

    int get payment => (parse_currency(payment_input.value) * 100).round();

    ElementList<PaymentSplit> get rows =>
            this.querySelectorAll(":scope tr.payment-split-row");

    PaymentSplitTable.created() : super.created(); attached() {
        TableRowElement totals = this.querySelector(":scope tr.split-table-totals");
        split_gross_total = totals.querySelector(":scope>.job-split");
        discount_gross_total = totals.querySelector(":scope>.job-discount");
        credit_gross_total = totals.querySelector(":scope>.job-credit");
        payment_input = document.querySelector('input[name="payment"]');
        payment_input.onKeyUp.listen(auto_split);
        discount_select = this.querySelector('select[name="discount"]');
        discount_select.onChange.listen(auto_split);
        discount_percent = double.parse(discount_select.value);
        tax_rate = double.parse(this.dataset['tax-rate']);
    }

    auto_split([Event e]) {
        discount_percent = double.parse(discount_select.value);
        var remaining = payment;
        for (PaymentSplit row in rows) {
            remaining = row.consume_payment(remaining);
        }
        recalculate();
    }

    recalculate() {

        Amount split_total = new Amount(0, 0, tax_rate),
               discount_total = new Amount(0, 0, tax_rate),
               credit_total = new Amount(0, 0, tax_rate);

        var rows = this.querySelectorAll(":scope tr.payment-split-row");
        for (PaymentSplit row in rows) {
            split_total += row.split_cell.amount;
            discount_total += row.discount_cell.amount;
            credit_total += row.credit_cell.amount;
        }

        split_gross_total.update(split_total);
        discount_gross_total.update(discount_total);
        credit_gross_total.update(credit_total);
    }

}

class PaymentSplit extends TableRowElement {

    PaymentSplitTable table;

    AmountViewCell balance_cell;
    AmountInputCell split_cell;
    AmountStatefulCell discount_cell;
    AmountViewCell credit_cell;

    PaymentSplit.created() : super.created(); attached() {
        table = parent.parent;
        balance_cell = this.querySelector(":scope>.job-balance");
        split_cell = this.querySelector(":scope>.job-split");
        split_cell.onAmountChange.listen(amount_changed);
        discount_cell = this.querySelector(":scope>.job-discount");
        credit_cell = this.querySelector(":scope>.job-credit");
    }

    amount_changed(AmountChangeEvent e) {

        if (e.is_gross) {
            // gross changes affect the discount
            var split_payment = split_cell.amount.gross;
            var tax_rate = split_cell.amount.tax_rate;
            var total = (split_payment / (1 - table.discount_percent)).round();
            var discount = new Amount.from_gross(total - split_payment, tax_rate);
            discount_cell.update(discount);
        }

        credit_cell.update(split_cell.amount + discount_cell.amount);

        table.recalculate();
    }

    int consume_payment(int payment) {

        Amount discount = balance_cell.amount * table.discount_percent;
        Amount apply = balance_cell.amount - discount;

        if (payment <= 0 || apply.gross <= 0) {
            split_cell.zero();
            discount_cell.zero();
            credit_cell.zero();
            return payment;
        }

        if (payment < apply.gross) {
            // available payment is less than expected
            // figure out a new total
            var total = (payment / (1 - table.discount_percent)).round();
            var tax_rate = split_cell.amount.tax_rate;
            apply = new Amount.from_gross(payment, tax_rate);
            discount = new Amount.from_gross(total - payment, tax_rate);
        }

        split_cell.update(apply);
        discount_cell.update(discount);
        credit_cell.update(apply + discount);

        return payment - apply.gross;
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('payment-split-table', PaymentSplitTable, extendsTag:'table');
    document.registerElement('payment-split', PaymentSplit, extendsTag:'tr');
}
