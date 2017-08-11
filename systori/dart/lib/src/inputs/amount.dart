import 'dart:html';
import 'dart:async';
import 'package:systori/numbers.dart';


abstract class AmountDivs {

    SpanElement _net_span;
    SpanElement _tax_span;
    SpanElement _gross_span;

    SpanElement _net_span_diff;
    SpanElement _tax_span_diff;
    SpanElement _gross_span_diff;

    DivElement _percent_div;

    String get _tax_rate;
    set _tax_rate(String tax_rate);

    updateViews(Amount amount) {
        _net_span.text = amount.net.money;
        _tax_span.text = amount.tax.money;
        _gross_span.text = amount.gross.money;
    }

    updateDiff(Amount amount) {
        _update_diff_value(_net_span_diff, amount.net);
        _update_diff_value(_tax_span_diff, amount.tax);
        _update_diff_value(_gross_span_diff, amount.gross);
    }

    _update_diff_value(SpanElement span, Decimal value) {
        span.classes.removeAll(['red', 'green']);
        if (value > new Decimal()) {
            span.text = '+' + value.money;
            span.classes.add('green');
        } else if (value < new Decimal()) {
            span.text = value.money;
            span.classes.add('red');
        }
    }

    updatePercent(double percent) {
        _percent_div.classes.removeAll(['red', 'green', 'blue']);
        int rounded = 0;
        if (percent < 100) {
            _percent_div.classes.add('blue');
            rounded = percent.floor();
        } else if (percent == 100.0) {
            _percent_div.classes.add('green');
            rounded = 100;
        } else if (percent > 100) {
            _percent_div.classes.add('red');
            rounded = percent.ceil();
        }
        _percent_div.text = "${rounded}%";
    }

    cacheViews(Element scope) {
        _gross_span = scope.querySelector(":scope>.amount-gross>.amount-value");
        _net_span = scope.querySelector(":scope>.amount-net>.amount-value");
        _tax_span = scope.querySelector(":scope>.amount-tax>.amount-value");
        _gross_span_diff = scope.querySelector(":scope>.amount-gross>.amount-diff");
        _net_span_diff = scope.querySelector(":scope>.amount-net>.amount-diff");
        _tax_span_diff = scope.querySelector(":scope>.amount-tax>.amount-diff");
        _percent_div = scope.querySelector(":scope>.amount-percent");
        _tax_rate = scope.dataset['tax-rate'];
    }

    Amount amountFromViews() =>
        new Amount.fromStringsZeroBlank(_net_span.text, _tax_span.text, _tax_rate);

}


abstract class AmountInputs {

    InputElement _net_input;
    InputElement _tax_input;
    InputElement _gross_input;

    String get _tax_rate;
    set _tax_rate(String tax_rate);

    updateInputs(Amount amount) {
        _net_input.value = amount.net.money;
        _tax_input.value = amount.tax.money;
        _gross_input.value = amount.gross.money;
    }

    cacheInputs(Element scope) {
        _gross_input = scope.querySelector(":scope>input.amount-gross");
        _net_input = scope.querySelector(":scope>input.amount-net");
        _tax_input = scope.querySelector(":scope>input.amount-tax");
        _tax_rate = scope.dataset['tax-rate'];
    }

    Amount amountFromInputs() =>
        new Amount.fromStringsZeroBlank(_net_input.value, _tax_input.value, _tax_rate);

}


abstract class AmountCell extends TableCellElement {

    Amount amount;

    AmountCell.created() : super.created();

    update(Amount amount);

    zero() => update(amount.zero());

}


class AmountViewCell extends AmountCell with AmountDivs {
    String _tax_rate;

    AmountViewCell.created() : super.created(); attached() {
        cacheViews(this);
        amount = amountFromViews();
    }

    update(Amount _amount) {
        amount = _amount;
        updateViews(_amount);
    }
}


enum AmountChangeType {
    NET, TAX, GROSS, ALL
}

class AmountChangeEvent {

    AmountChangeType type;
    Decimal old_value;
    Decimal new_value;

    bool get isNet => type == AmountChangeType.NET;
    bool get isTax => type == AmountChangeType.TAX;
    bool get isGross => type == AmountChangeType.GROSS;

    AmountChangeEvent(this.type, this.old_value, this.new_value);

}


class AmountInputCell extends AmountCell with AmountInputs {

    String _tax_rate;

    StreamController<AmountChangeEvent> controller = new StreamController<AmountChangeEvent>();
    get onAmountChange => controller.stream;

    AmountInputCell.created() : super.created(); attached() {
        cacheInputs(this);
        amount = amountFromInputs();
        _gross_input.onKeyUp.listen(grossChanged);
        _net_input.onKeyUp.listen(netChanged);
        _tax_input.onKeyUp.listen(taxChanged);
    }

    update(Amount _amount, {bool triggerEvent: false}) {
        amount = _amount;
        updateInputs(_amount);
        if (triggerEvent) {
            controller.add(new AmountChangeEvent(AmountChangeType.ALL, null, null));
        }
    }

    grossChanged([Event _]) {
        Decimal value = new Decimal.parse(_gross_input.value);
        var event = new AmountChangeEvent(AmountChangeType.GROSS, amount.gross, value);
        amount = amount.adjustGross(value);
        _net_input.value = amount.net.money;
        _tax_input.value = amount.tax.money;
        controller.add(event);
    }

    netChanged([Event _]) {
        Decimal value = new Decimal.parse(_net_input.value);
        var event = new AmountChangeEvent(AmountChangeType.NET, amount.net, value);
        amount = amount.adjustNet(value);
        _tax_input.value = amount.tax.money;
        _gross_input.value = amount.gross.money;
        controller.add(event);
    }

    taxChanged([Event _]) {
        Decimal value = new Decimal.parse(_tax_input.value);
        value = value.isNotNull ? value : new Decimal();
        var event = new AmountChangeEvent(AmountChangeType.TAX, amount.tax, value);
        amount = amount.adjustTax(value);
        _net_input.value = amount.net.money;
        _gross_input.value = amount.gross.money;
        controller.add(event);
    }

}


class AmountStatefulCell extends AmountCell with AmountDivs, AmountInputs {

    String _tax_rate;

    AmountStatefulCell.created() : super.created(); attached() {
        cacheViews(this);
        cacheInputs(this);
        amount = amountFromInputs();
    }

    update(Amount _amount) {
        amount = _amount;
        updateViews(_amount);
        updateInputs(_amount);
    }
}


registerAmountElements() {
    document.registerElement('amount-view', AmountViewCell, extendsTag:'td');
    document.registerElement('amount-input', AmountInputCell, extendsTag:'td');
    document.registerElement('amount-stateful', AmountStatefulCell, extendsTag:'td');
}
