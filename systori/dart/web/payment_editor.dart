import 'dart:html';
import 'package:intl/intl.dart';
import 'package:systori/inputs.dart';
import 'package:systori/numbers.dart';


class PaymentSplitTable extends TableElement {

    TextInputElement payment_input;
    SelectElement discount_select;

    AmountViewCell split_gross_total;
    AmountViewCell discount_gross_total;
    AmountViewCell credit_gross_total;

    Decimal discount_percent;
    Amount tax_rate;

    Decimal get payment => new Decimal.parse(payment_input.value);

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
        discount_percent = new Decimal(double.parse(discount_select.value));
        tax_rate = new Amount.fromStrings('0', '0', this.dataset['tax-rate']);
    }

    auto_split([Event e]) {
        discount_percent = new Decimal(double.parse(discount_select.value));
        var remaining = payment;
        for (PaymentSplit row in rows) {
            remaining = row.consume_payment(remaining);
        }
        recalculate();
    }

    recalculate() {

        Amount split_total = tax_rate.zero(),
               discount_total = tax_rate.zero(),
               credit_total = tax_rate.zero();

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

        var split_payment = split_cell.amount.gross;
        var tax_rate = split_cell.amount.tax_rate;
        var total = (split_payment / (new Decimal(1) - table.discount_percent));
        var discount = new Amount.fromGross(
                total - split_payment,
                split_cell.amount.tax.isZero ? new Decimal(0) : tax_rate
        );

        discount_cell.update(discount);
        credit_cell.update(split_cell.amount + discount_cell.amount);

        table.recalculate();
    }

    Decimal consume_payment(Decimal payment) {

        Amount discount = balance_cell.amount * table.discount_percent;
        Amount apply = balance_cell.amount - discount;

        if (payment.decimal <= 0 || apply.gross.decimal <= 0) {
            split_cell.zero();
            discount_cell.zero();
            credit_cell.zero();
            return payment;
        }

        if (payment < apply.gross) {
            // available payment is less than expected
            // figure out a new total
            var total = (payment / (new Decimal(1) - table.discount_percent));
            var tax_rate =
                balance_cell.amount.gross.isNonzero && balance_cell.amount.tax.isZero
                        ? new Decimal()
                        : split_cell.amount.tax_rate;
            apply = new Amount.fromGross(payment, tax_rate);
            discount = new Amount.fromGross(total - payment, tax_rate);
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
