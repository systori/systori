import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat SPLIT = new NumberFormat("#,###,###,##0.00");

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;

    InputElement payment_input = querySelector('input[name="amount"]');

    payment_input.onKeyUp.listen((e) {
        double payment = parse_decimal(payment_input.value);
        var splits = querySelectorAll('[name^="split-"][name\$="-amount"]');
        int split_amount = payment / splits.length;
        splits.forEach((e) {
            e.value = SPLIT.format(split_amount);
        });
    });
}
