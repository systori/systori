import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");

int amount_string_to_int(amount) {
    return (double.parse(amount) * 100).round();
}


class PaymentSplitTable extends TableElement {

    TextInputElement payment_input;
    SelectElement discount_select;
    CheckboxInputElement adjustment_checkbox;

    TableCellElement payment_gross_total;
    TableCellElement discount_gross_total;
    TableCellElement adjustment_gross_total;
    TableCellElement credit_gross_total;

    double discount_percent;
    bool is_auto_adjusted;

    PaymentSplitTable.created() : super.created() {
        TableRowElement totals = this.querySelector(":scope tr.split-table-totals");
        this.payment_gross_total = totals.querySelector(":scope>.job-payment");
        this.discount_gross_total = totals.querySelector(":scope>.job-discount");
        this.adjustment_gross_total = totals.querySelector(":scope>.job-adjustment");
        this.credit_gross_total = totals.querySelector(":scope>.job-credit");
        payment_input = document.querySelector('input[name="amount"]');
        payment_input.onKeyUp.listen(update_table);
        discount_select = this.querySelector('select[name="discount"]');
        discount_select.onChange.listen(update_table);
        discount_percent = double.parse(discount_select.value);
        adjustment_checkbox = this.querySelector('input[name="is_adjusted"]');
        adjustment_checkbox.onChange.listen(update_table);
        is_auto_adjusted = adjustment_checkbox.checked;
    }

    update_table(Event e) {
        discount_percent = double.parse(discount_select.value);
        is_auto_adjusted = adjustment_checkbox.checked;
        int remaining = (parse_currency(payment_input.value) * 100).round();
        var rows = this.querySelectorAll(":scope tr.payment-split-row");
        for (PaymentSplit row in rows) {
            remaining = row.consume_payment(remaining, discount_percent);
        }
        recalculate();
    }

    recalculate() {

        int payment_gross = 0,
            discount_gross = 0,
            adjustment_gross = 0,
            credit_gross = 0;

        var rows = this.querySelectorAll(":scope tr.payment-split-row");
        for (PaymentSplit row in rows) {
            payment_gross += row.payment_gross;
            discount_gross += row.discount_gross;
            adjustment_gross += row.adjustment_gross;
            credit_gross += row.credit_gross;
        }

        payment_gross_total.text = AMOUNT.format(payment_gross/100);
        discount_gross_total.text = AMOUNT.format(discount_gross/100);
        adjustment_gross_total.text = AMOUNT.format(adjustment_gross/100);
        credit_gross_total.text = AMOUNT.format(credit_gross/100);
    }

}

class PaymentSplit extends TableRowElement {

    TextInputElement payment_input;
    HiddenInputElement discount_input;
    TextInputElement adjustment_input;

    SpanElement payment_span;
    SpanElement discount_span;
    TableCellElement credit_cell;

    // 1.00 -> 100
    int balance_gross;
    int payment_gross;
    int discount_gross;
    int adjustment_gross;
    int credit_gross;

    PaymentSplit.created() : super.created() {

        TableCellElement balance_cell = this.querySelector(":scope>.job-balance");
        this.balance_gross = amount_string_to_int(balance_cell.dataset['amount']);

        TableCellElement payment_cell = this.querySelector(":scope>.job-payment");
        this.payment_input = this.querySelector('[name^="split-"][name\$="-payment"]');
        this.payment_input.onKeyUp.listen(input_changed);
        this.payment_gross = amount_string_to_int(payment_cell.dataset['amount']);

        TableCellElement discount_cell = this.querySelector(":scope>.job-discount");
        this.discount_input = this.querySelector('[name^="split-"][name\$="-discount"]');
        this.discount_span = discount_cell.querySelector('.text');
        this.discount_gross = amount_string_to_int(discount_cell.dataset['amount']);

        TableCellElement adjustment_cell = this.querySelector(":scope>.job-adjustment");
        this.adjustment_input = this.querySelector('[name^="split-"][name\$="-adjustment"]');
        this.adjustment_input.onKeyUp.listen(input_changed);
        this.adjustment_gross = amount_string_to_int(adjustment_cell.dataset['amount']);

        credit_cell = this.querySelector(":scope>.job-credit");
        this.credit_gross = amount_string_to_int(credit_cell.dataset['amount']);

    }

    input_changed([Event e]) {
        PaymentSplitTable table = parent.parent as PaymentSplitTable;

        payment_gross = (parse_currency(payment_input.value) * 100).round();

        int full_amount = (payment_gross/(1-table.discount_percent)).round();
        discount_gross = full_amount - payment_gross;
        discount_input.value = (discount_gross/100).toStringAsFixed(2);
        discount_span.text = AMOUNT.format(discount_gross/100);

        adjustment_gross = 0;
        if (table.is_auto_adjusted) {
            var possible_adjustment = balance_gross - (payment_gross + discount_gross);
            adjustment_gross = possible_adjustment > 0 ? possible_adjustment : 0;
        }
        adjustment_input.value = AMOUNT.format(adjustment_gross/100);

        credit_gross = payment_gross + discount_gross + adjustment_gross;
        credit_cell.text = AMOUNT.format(credit_gross/100);

        if (e != null) table.recalculate();
    }

    int consume_payment(int payment, double discount) {
        int expected_payment = (balance_gross * (1-discount)).round();
        if (payment <= 0) {
            payment_input.value = AMOUNT.format(0);
        } else if (payment < expected_payment){
            payment_input.value = AMOUNT.format(payment/100);
            payment = 0;
        } else {
            payment_input.value = AMOUNT.format(expected_payment/100);
            payment -= expected_payment;
        }
        input_changed();
        return payment;
    }

}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('payment-split-table', PaymentSplitTable, extendsTag:'table');
    document.registerElement('payment-split', PaymentSplit, extendsTag:'tr');
}

