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
    int gross;
    double tax_rate;

    String get net_string => amount_int_to_string(net);
    String get tax_string => amount_int_to_string(tax);
    String get gross_string => amount_int_to_string(gross);

    Amount(this.net, this.tax, this.gross, this.tax_rate);

    Amount.from_strings(String net, String tax, String gross, String rate): this(
        amount_string_to_int(net),
        amount_string_to_int(tax),
        amount_string_to_int(gross),
        double.parse(rate)
    );

    Amount operator * (num multiple) {
        var result = new Amount(
            (net*multiple).round(), 0,
            (gross*multiple).round(), tax_rate
        );
        result.tax = result.gross - result.net;
        return result;
    }

    Amount operator - (Amount other) {
        return new Amount(
            net - other.net,
            tax - other.tax,
            gross - other.gross,
            tax_rate
        );
    }

    Amount operator + (Amount other) {
        return new Amount(
            net + other.net,
            tax + other.tax,
            gross + other.gross,
            tax_rate
        );
    }

    update_gross(int _gross) {
        gross = _gross;
        net = (gross / (1+tax_rate)).round();
        tax = gross - net;
    }

    update_net(int _net) {
        net = _net;
        tax = gross - net;
    }

    update_tax(int _tax) {
        tax = _tax;
        net = gross - tax;
    }

    zero() { net = tax = gross = 0; }

}


class AmountDivs {

    DivElement _net_div;
    DivElement _tax_div;
    DivElement _gross_div;

    String _tax_rate;

    update_divs(Amount amount) {
        _net_div.text = amount.net_string;
        _tax_div.text = amount.tax_string;
        _gross_div.text = amount.gross_string;
    }

    cache_divs(Element scope) {
        _gross_div = scope.querySelector(":scope>div.amount-gross");
        _net_div = scope.querySelector(":scope>div.amount-net");
        _tax_div = scope.querySelector(":scope>div.amount-tax");
        _tax_rate = scope.dataset['tax-rate'];
    }

    Amount amount_from_divs() =>
        new Amount.from_strings(
                _net_div.text,
                _tax_div.text,
                _gross_div.text,
                _tax_rate
        );

}


class AmountViewCell extends TableCellElement with AmountDivs {

    Amount amount;

    AmountViewCell.created() : super.created(); attached() {
        cache_divs(this);
        amount = amount_from_divs();
    }

    update(Amount _amount) {
        amount = _amount;
        update_divs(_amount);
    }
}


class AmountInputs {

    InputElement _net_input;
    InputElement _tax_input;
    InputElement _gross_input;

    String _tax_rate;

    update_inputs(Amount amount) {
        _net_input.text = amount.net_string;
        _tax_input.text = amount.tax_string;
        _gross_input.text = amount.gross_string;
    }

    cache_inputs(Element scope) {
        _gross_input = scope.querySelector(":scope>input.amount-gross");
        _net_input = scope.querySelector(":scope>input.amount-net");
        _tax_input = scope.querySelector(":scope>input.amount-tax");
        _tax_rate = scope.dataset['tax-rate'];
    }

    Amount amount_from_inputs() =>
        new Amount.from_strings(
                _net_input.value,
                _tax_input.value,
                _gross_input.value,
                _tax_rate
        );

}


class AmountInputCell extends TableCellElement with AmountInputs {

    StreamController<Event> controller = new StreamController<Event>();
    get onAmountChange => controller.stream;

    Amount amount;

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

    gross_changed([Event e]) {
        int value = amount_string_to_int(_gross_input.value);
        amount.update_gross(value);
        update_inputs(amount);
        controller.add(e);
    }

    net_changed([Event e]) {
        int value = amount_string_to_int(_net_input.value);
        amount.update_net(value);
        update_inputs(amount);
        controller.add(e);
    }

    tax_changed([Event e]) {
        int value = amount_string_to_int(_tax_input.value);
        amount.update_tax(value);
        update_inputs(amount);
        controller.add(e);
    }

}


class AmountStatefulCell extends TableCellElement with AmountDivs, AmountInputs {

    Amount amount;

    AmountStatefulCell.created() : super.created(); attached() {
        cache_divs(this);
        cache_inputs(this);
        amount = amount_from_inputs();
    }

    update(Amount _amount) {
        amount = _amount;
        update_divs(_amount);
        update_inputs(_amount);
    }
}


registerAmountElements() {
    document.registerElement('amount-view', AmountViewCell, extendsTag:'td');
    document.registerElement('amount-input', AmountInputCell, extendsTag:'td');
    document.registerElement('amount-stateful', AmountStatefulCell, extendsTag:'td');
}
