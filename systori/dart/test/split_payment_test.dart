import 'dart:html';
import 'package:test/test.dart';
import '../web/amount_element.dart';
import '../web/split_payment.dart' as split_payment;

void main() {
    split_payment.main();
    test("check that AmountViewCell is registered", () {
        AmountViewCell balance = querySelector('td[is="amount-view"]');
        expect("480,00", equals(balance.gross_div.text));
    });
}
