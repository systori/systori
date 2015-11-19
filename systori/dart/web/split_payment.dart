import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat SPLIT = new NumberFormat("#,###,###,##0.00");

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;

    InputElement payment_input = querySelector('input[name="amount"]');

    payment_input.onKeyUp.listen((e) {
        double payment = parse_decimal(payment_input.value);
        querySelectorAll('[name^="split-"][name\$="-amount"]').forEach((e) {
            double ratio = double.parse(e.parent.dataset['ratio']);
            e.value = SPLIT.format(payment * ratio);
        });
    });
}
