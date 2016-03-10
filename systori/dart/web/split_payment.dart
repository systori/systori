import 'dart:html';
import 'dart:async';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");

int amount_string_to_int(amount) {
    return (double.parse(amount) * 100).round();
}


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
            remaining = row.consume_payment(remaining, discount_percent);
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
            discount_gross += row.discount_gross;
            credit_gross += row.credit_gross;
        }

        payment_gross_total.text = AMOUNT.format(payment_gross/100);
        discount_gross_total.text = AMOUNT.format(discount_gross/100);
        credit_gross_total.text = AMOUNT.format(credit_gross/100);
    }

}

class PaymentSplit extends TableRowElement {

    AmountCell payment_cell;
    HiddenInputElement discount_input_gross;
    HiddenInputElement discount_input_net;
    HiddenInputElement discount_input_tax;

    SpanElement payment_span;
    SpanElement discount_span;
    TableCellElement credit_cell;

    // 1.00 -> 100
    int balance_gross;
    int payment_gross;
    int discount_gross;
    int credit_gross;

    PaymentSplit.created() : super.created() {

        this.payment_cell = this.querySelector(":scope>.job-payment");
        //this.payment_cell.onAmountChange.listen(input_changed);

        TableCellElement balance_cell = this.querySelector(":scope>.job-balance");
        this.balance_gross = amount_string_to_int(balance_cell.dataset['amount']);

        TableCellElement discount_cell = this.querySelector(":scope>.job-discount");
        this.discount_input_gross = this.querySelector('[name^="split-"][name\$="-discount_gross"]');
        this.discount_input_net = this.querySelector('[name^="split-"][name\$="-discount_net"]');
        this.discount_input_tax = this.querySelector('[name^="split-"][name\$="-discount_tax"]');
        this.discount_span = discount_cell.querySelector('.text');
        this.discount_gross = amount_string_to_int(discount_cell.dataset['amount']);

        credit_cell = this.querySelector(":scope>.job-credit");
        this.credit_gross = amount_string_to_int(credit_cell.dataset['amount']);

    }

    input_changed([Event e]) {
        PaymentSplitTable table = parent.parent as PaymentSplitTable;

        payment_gross = payment_cell.gross;

        int full_amount = (payment_gross/(1-table.discount_percent)).round();
        discount_gross = full_amount - payment_gross;
        discount_input_gross.value = (discount_gross/100).toStringAsFixed(2);
        int _tax = (discount_gross / payment_cell.inverse_tax_rate).round();
        discount_input_tax.value = (_tax/100).toStringAsFixed(2);
        discount_input_net.value = ((discount_gross-_tax)/100).toStringAsFixed(2);
        discount_span.text = AMOUNT.format(discount_gross/100);

        credit_gross = payment_gross + discount_gross;
        credit_cell.text = AMOUNT.format(credit_gross/100);

        if (e != null) table.recalculate();
    }

    int consume_payment(int payment, double discount) {
        int expected_payment = (balance_gross * (1-discount)).round();
        if (payment <= 0 || expected_payment < 0) {
            payment_cell.gross = 0;
        } else if (payment < expected_payment){
            payment_cell.gross = payment;
            payment = 0;
        } else {
            payment_cell.gross = expected_payment;
            payment -= expected_payment;
        }
        payment_cell.recalculate_net_tax();
        input_changed();
        return payment;
    }

}

class AmountCell extends TableCellElement {

    StreamController<Event> controller = new StreamController<Event>();
    get onAmountChange => controller.stream;

    TextInputElement gross_input;

    int get gross => (parse_currency(gross_input.value) * 100).round();
    void set gross(int _gross) {
        gross_input.value = AMOUNT.format(_gross/100);
    }

    TextInputElement net_input;

    int get net => (parse_currency(net_input.value) * 100).round();
    void set net(int _net) {
        net_input.value = AMOUNT.format(_net/100);
    }

    TextInputElement tax_input;

    int get tax => (parse_currency(tax_input.value) * 100).round();
    void set tax(int _tax) {
        tax_input.value = AMOUNT.format(_tax/100);
    }

    double tax_rate;
    double inverse_tax_rate;

    AmountCell.created() : super.created() {
        tax_rate = double.parse(this.dataset['tax-rate']);
        inverse_tax_rate = 1.0 + (1.0 / tax_rate);
        gross_input = this.querySelector(":scope>.amount-gross");
        gross_input.onKeyUp.listen(gross_changed);
        net_input = this.querySelector(":scope>.amount-net");
        net_input.onKeyUp.listen(net_changed);
        tax_input = this.querySelector(":scope>.amount-tax");
        tax_input.onKeyUp.listen(tax_changed);
        (this.parent as PaymentSplit).payment_cell = this;
        onAmountChange.listen((this.parent as PaymentSplit).input_changed);
    }

    recalculate_net_tax() {
        tax = (gross / inverse_tax_rate).round();
        net = gross - tax;
    }

    gross_changed([Event e]) {
        recalculate_net_tax();
        controller.add(e);
    }

    net_changed([Event e]) {
        tax = (net * tax_rate).round();
        gross = tax + net;
        controller.add(e);
    }

    tax_changed([Event e]) {
        net = (tax / tax_rate).round();
        gross = net + tax;
        controller.add(e);
    }

}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('payment-split-table', PaymentSplitTable, extendsTag:'table');
    document.registerElement('payment-split', PaymentSplit, extendsTag:'tr');
    document.registerElement('amount-cell', AmountCell, extendsTag:'td');
}

