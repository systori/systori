import 'dart:html';
import 'dart:async';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");

int amount_string_to_int(String amount) =>
    (parse_currency(amount) * 100).round();

String amount_int_to_string(int amount) =>
    AMOUNT.format(amount / 100);


class Amount {

    int net;
    int tax;
    int get gross => net + tax;
    double tax_rate;

    String get net_string => amount_int_to_string(net);
    String get tax_string => amount_int_to_string(tax);
    String get gross_string => amount_int_to_string(gross);

    void set gross(int _gross) {
        net = (_gross / (1+tax_rate)).round();
        tax = _gross - net;
    }

    adjust_net(int _net) {
        tax = gross - _net;
        net = _net;
    }

    adjust_tax(int _tax) {
        net = gross - _tax;
        tax = _tax;
    }

    Amount(this.net, this.tax, this.tax_rate);

    Amount.from_strings(String net, String tax, String rate): this(
        amount_string_to_int(net),
        amount_string_to_int(tax),
        double.parse(rate)
    );

    Amount.from_gross(int _gross, double _tax_rate) {
        tax_rate = _tax_rate;
        gross = _gross;
    }

    Amount.zeroed() { zero(); }

    Amount operator * (num multiple) =>
        new Amount((net * multiple).round(), (tax * multiple).round(), tax_rate);

    Amount operator - (Amount other) =>
        new Amount(net - other.net, tax - other.tax, tax_rate);

    Amount operator + (Amount other) =>
        new Amount(net + other.net, tax + other.tax, tax_rate);

    zero() { net = tax = 0; }

    zero_negatives() {
        if (net < 0) net = 0;
        if (tax < 0) tax = 0;
    }

}


class AmountDivs {

    SpanElement _net_span;
    SpanElement _tax_span;
    SpanElement _gross_span;

    SpanElement _net_span_diff;
    SpanElement _tax_span_diff;
    SpanElement _gross_span_diff;

    String _tax_rate;

    update_views(Amount amount) {
        _net_span.text = amount.net_string;
        _tax_span.text = amount.tax_string;
        _gross_span.text = amount.gross_string;
    }

    update_diff(Amount amount) {
        _update_diff_value(_net_span, amount.net, amount.net_string);
        _update_diff_value(_tax_span, amount.tax, amount.tax_string);
        _update_diff_value(_gross_span, amount.gross, amount.gross_string);
    }

    _update_diff_value(SpanElement span, int value, String value_str) {
        span.classes.removeAll(['red', 'green']);
        if (value > 0) {
            span.text = '+' + value_str;
            span.classes.add('green');
        } else if (value < 0) {
            span.text = value_str;
            span.classes.add('red');
        }

    }

    cache_views(Element scope) {
        _gross_span = scope.querySelector(":scope>.amount-gross>.amount-value");
        _net_span = scope.querySelector(":scope>.amount-net>.amount-value");
        _tax_span = scope.querySelector(":scope>.amount-tax>.amount-value");
        _gross_span_diff = scope.querySelector(":scope>.amount-gross>.amount-diff");
        _net_span_diff = scope.querySelector(":scope>.amount-net>.amount-diff");
        _tax_span_diff = scope.querySelector(":scope>.amount-tax>.amount-diff");
        _tax_rate = scope.dataset['tax-rate'];
    }

    Amount amount_from_views() =>
        new Amount.from_strings(_net_span.text, _tax_span.text, _tax_rate);

}


class AmountInputs {

    InputElement _net_input;
    InputElement _tax_input;
    InputElement _gross_input;

    String _tax_rate;

    update_inputs(Amount amount) {
        _net_input.value = amount.net_string;
        _tax_input.value = amount.tax_string;
        _gross_input.value = amount.gross_string;
    }

    cache_inputs(Element scope) {
        _gross_input = scope.querySelector(":scope>input.amount-gross");
        _net_input = scope.querySelector(":scope>input.amount-net");
        _tax_input = scope.querySelector(":scope>input.amount-tax");
        _tax_rate = scope.dataset['tax-rate'];
    }

    Amount amount_from_inputs() =>
        new Amount.from_strings(_net_input.value, _tax_input.value, _tax_rate);

}


abstract class AmountCell extends TableCellElement {

    Amount amount;

    AmountCell.created() : super.created();

    update(Amount _amount);

    zero() {
        amount.zero();
        update(amount);
    }
}


class AmountViewCell extends AmountCell with AmountDivs {

    AmountViewCell.created() : super.created(); attached() {
        cache_views(this);
        amount = amount_from_views();
    }

    update(Amount _amount) {
        amount = _amount;
        update_views(_amount);
    }
}


enum AmountChangeType {
    NET, TAX, GROSS
}

class AmountChangeEvent {

    AmountChangeType type;
    int old_value;
    int new_value;

    bool get is_net => type == AmountChangeType.NET;
    bool get is_tax => type == AmountChangeType.TAX;
    bool get is_gross => type == AmountChangeType.GROSS;

    AmountChangeEvent(this.type, this.old_value, this.new_value);

}


class AmountInputCell extends AmountCell with AmountInputs {

    StreamController<AmountChangeEvent> controller = new StreamController<AmountChangeEvent>();
    get onAmountChange => controller.stream;

    AmountInputCell.created() : super.created(); attached() {
        cache_inputs(this);
        amount = amount_from_inputs();
        _gross_input.onKeyUp.listen(gross_changed);
        _net_input.onKeyUp.listen(net_changed);
        _tax_input.onKeyUp.listen(tax_changed);
    }

    update(Amount _amount) {
        amount = _amount;
        update_inputs(_amount);
    }

    gross_changed([Event _]) {
        int value = amount_string_to_int(_gross_input.value);
        var event = new AmountChangeEvent(AmountChangeType.GROSS, amount.gross, value);
        amount.gross = value;
        _net_input.value = amount.net_string;
        _tax_input.value = amount.tax_string;
        controller.add(event);
    }

    net_changed([Event _]) {
        int value = amount_string_to_int(_net_input.value);
        var event = new AmountChangeEvent(AmountChangeType.NET, amount.net, value);
        amount.adjust_net(value);
        _tax_input.value = amount.tax_string;
        _gross_input.value = amount.gross_string;
        controller.add(event);
    }

    tax_changed([Event _]) {
        int value = amount_string_to_int(_tax_input.value);
        var event = new AmountChangeEvent(AmountChangeType.TAX, amount.tax, value);
        amount.adjust_tax(value);
        _net_input.value = amount.net_string;
        _gross_input.value = amount.gross_string;
        controller.add(event);
    }

}


class AmountStatefulCell extends AmountCell with AmountDivs, AmountInputs {

    AmountStatefulCell.created() : super.created(); attached() {
        cache_views(this);
        cache_inputs(this);
        amount = amount_from_inputs();
    }

    update(Amount _amount) {
        amount = _amount;
        update_views(_amount);
        update_inputs(_amount);
    }
}


registerAmountElements() {
    document.registerElement('amount-view', AmountViewCell, extendsTag:'td');
    document.registerElement('amount-input', AmountInputCell, extendsTag:'td');
    document.registerElement('amount-stateful', AmountStatefulCell, extendsTag:'td');
}
