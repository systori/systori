import 'dart:html';
import 'dart:async';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");

int amount_string_to_int(String amount) =>
    (parse_currency(amount) * 100).round();

String amount_int_to_string(int amount) =>
    AMOUNT.format(amount / 100);


class AmountInputCell extends TableCellElement {

    StreamController<Event> controller = new StreamController<Event>();
    get onAmountChange => controller.stream;

    TextInputElement gross_input;

    int get gross => amount_string_to_int(gross_input.value);
    void set gross(int _gross) {
        gross_input.value = amount_int_to_string(_gross);
    }

    TextInputElement net_input;

    int get net => amount_string_to_int(net_input.value);
    void set net(int _net) {
        net_input.value = amount_int_to_string(_net);
    }

    TextInputElement tax_input;

    int get tax => amount_string_to_int(tax_input.value);
    void set tax(int _tax) {
        tax_input.value = amount_int_to_string(_tax);
    }

    zero() { tax = net = gross = 0; }

    double tax_rate;
    double inverse_tax_rate;

    AmountInputCell.created() : super.created() {
        tax_rate = double.parse(this.dataset['tax-rate']);
        inverse_tax_rate = 1.0 + (1.0 / tax_rate);
        gross_input = this.querySelector(":scope>.amount-gross");
        gross_input.onKeyUp.listen(gross_changed);
        net_input = this.querySelector(":scope>.amount-net");
        net_input.onKeyUp.listen(net_changed);
        tax_input = this.querySelector(":scope>.amount-tax");
        tax_input.onKeyUp.listen(tax_changed);
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


class AmountViewCell extends TableCellElement {

    SpanElement gross_span;

    int get gross => amount_string_to_int(gross_span.text);
    void set gross(int _gross) {
        gross_span.text = amount_int_to_string(_gross);
    }

    SpanElement net_span;

    int get net => amount_string_to_int(net_span.text);
    void set net(int _net) {
        net_span.text = amount_int_to_string(_net);
    }

    SpanElement tax_span;

    int get tax => amount_string_to_int(tax_span.text);
    void set tax(int _tax) {
        tax_span.text = amount_int_to_string(_tax);
    }

    zero() { tax = net = gross = 0; }

    AmountViewCell.created() : super.created() {
        gross_span = this.querySelector(":scope>span.amount-gross");
        net_span = this.querySelector(":scope>span.amount-net");
        tax_span = this.querySelector(":scope>span.amount-tax");
    }

}


class AmountViewInputCell extends AmountViewCell {

    HiddenInputElement gross_input;

    int get gross => amount_string_to_int(gross_input.value);
    void set gross(int _gross) {
        gross_input.value = gross_span.text = amount_int_to_string(_gross);
    }

    HiddenInputElement net_input;

    int get net => amount_string_to_int(net_input.value);
    void set net(int _net) {
        net_input.value = net_span.text = amount_int_to_string(_net);
    }

    HiddenInputElement tax_input;

    int get tax => amount_string_to_int(tax_input.value);
    void set tax(int _tax) {
        tax_input.value = tax_span.text = amount_int_to_string(_tax);
    }

    zero() { tax = net = gross = 0; }

    AmountViewInputCell.created() : super.created() {
        gross_input = this.querySelector(":scope>input.amount-gross");
        net_input = this.querySelector(":scope>input.amount-net");
        tax_input = this.querySelector(":scope>input.amount-tax");
    }
}

registerAmountElements() {
    document.registerElement('amount-input', AmountInputCell, extendsTag:'td');
    document.registerElement('amount-view', AmountViewCell, extendsTag:'td');
    document.registerElement('amount-view-input', AmountViewInputCell, extendsTag:'td');
}
