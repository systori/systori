import 'dart:html';
import 'package:test/test.dart';
import '../web/split_payment.dart';
import '../web/split_payment.dart' as split_payment;

void main() { split_payment.main();

    group("PaymentSplitTable", () {

        test("is registered", () {
            PaymentSplitTable table = querySelector("table");
            expect(table.rows.length, equals(2));
        });

        test("auto_split()", () {

            InputElement input = querySelector('#id_amount');
            input.value = '500,00';

            PaymentSplitTable table = querySelector("table");
            PaymentSplit row = table.rows.first;

            expect(row.payment_cell.amount.net_string, equals('0,00'));

            table.auto_split();

            expect(row.payment_cell.amount.net_string, equals('388,80'));

        });

    });

}
