@TestOn('browser')
import 'dart:html';
import 'package:test/test.dart';
import 'package:systori/numbers.dart';
import '../../web/payment_editor.dart';
import '../../web/payment_editor.dart' as payment_editor;

void main() { payment_editor.main();

    group("PaymentTable", () {

        InputElement amount_input = querySelector('#id_payment');
        SelectElement discount_input = querySelector('#id_discount');
        PaymentSplitTable table = querySelector("table");

        setUp(() {
            amount_input.value = '0,00';
            discount_input.selectedIndex = 0;
            table.auto_split();
        });

        test("is registered", () {
            PaymentSplitTable table = querySelector("table");
            expect(table.rows.length, equals(2));
        });

        test("auto_split()", () {

            amount_input.value = '500,00';

            PaymentSplit row = table.rows.first;

            expect(row.split_cell.amount.net.money, equals('0,00'));
            expect(row.split_cell.amount.tax.money, equals('0,00'));
            expect(row.split_cell.amount.gross.money, equals('0,00'));

            table.auto_split();

            expect(row.split_cell.amount.net.money, equals('388,80'));
            expect(row.split_cell.amount.tax.money, equals('91,20'));
            expect(row.split_cell.amount.gross.money, equals('480,00'));
            expect(row.discount_cell.amount.net.money, equals('0,00'));
            expect(row.discount_cell.amount.tax.money, equals('0,00'));
            expect(row.discount_cell.amount.gross.money, equals('0,00'));
            row = table.rows[1];
            expect(row.split_cell.amount.net.money, equals('16,807'));
            expect(row.split_cell.amount.tax.money, equals('3,193'));
            expect(row.split_cell.amount.gross.money, equals('20,00'));
            expect(row.discount_cell.amount.net.money, equals('0,00'));
            expect(row.discount_cell.amount.tax.money, equals('0,00'));
            expect(row.discount_cell.amount.gross.money, equals('0,00'));

        });

        test("auto_split() with 1% discount", () {

            amount_input.value = '500,00';
            discount_input.selectedIndex = 1;

            PaymentSplit row = table.rows.first;

            expect(row.split_cell.amount.net.money, equals('0,00'));
            expect(row.split_cell.amount.tax.money, equals('0,00'));
            expect(row.split_cell.amount.gross.money, equals('0,00'));

            table.auto_split();

            expect(row.split_cell.amount.net.money, equals('384,912'));
            expect(row.split_cell.amount.tax.money, equals('90,288'));
            expect(row.split_cell.amount.gross.money, equals('475,20'));
            expect(row.discount_cell.amount.net.money, equals('3,888'));
            expect(row.discount_cell.amount.tax.money, equals('0,912'));
            expect(row.discount_cell.amount.gross.money, equals('4,80'));
            row = table.rows[1];
            expect(row.split_cell.amount.net.money, equals('20,84'));
            expect(row.split_cell.amount.tax.money, equals('3,96'));
            expect(row.split_cell.amount.gross.money, equals('24,80'));
            expect(row.discount_cell.amount.net.money, equals('0,211'));
            expect(row.discount_cell.amount.tax.money, equals('0,04'));
            expect(row.discount_cell.amount.gross.money, equals('0,251'));

        });

        test("recalculate() totals", () {

            amount_input.value = '500,00';
            discount_input.selectedIndex = 1;
            table.auto_split();

            Amount payment_total = table.split_gross_total.amount;
            expect(payment_total.net.money, equals('405,752'));
            expect(payment_total.tax.money, equals('94,248'));
            expect(payment_total.gross.money, equals('500,00'));

            Amount discount_total = table.discount_gross_total.amount;
            expect(discount_total.net.money, equals('4,099'));
            expect(discount_total.tax.money, equals('0,952'));
            expect(discount_total.gross.money, equals('5,051'));

            Amount credit_total = table.credit_gross_total.amount;
            expect(credit_total.net.money, equals('409,851'));
            expect(credit_total.tax.money, equals('95,20'));
            expect(credit_total.gross.money, equals('505,051'));
        });

    });

}
