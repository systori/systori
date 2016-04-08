import 'dart:html';
import 'package:test/test.dart';
import '../web/amount_element.dart' show Amount;
import '../web/payment_editor.dart';
import '../web/payment_editor.dart' as payment_editor;

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

            expect(row.split_cell.amount.net_string, equals('0,00'));
            expect(row.split_cell.amount.tax_string, equals('0,00'));
            expect(row.split_cell.amount.gross_string, equals('0,00'));

            table.auto_split();

            expect(row.split_cell.amount.net_string, equals('388,80'));
            expect(row.split_cell.amount.tax_string, equals('91,20'));
            expect(row.split_cell.amount.gross_string, equals('480,00'));
            expect(row.discount_cell.amount.net_string, equals('0,00'));
            expect(row.discount_cell.amount.tax_string, equals('0,00'));
            expect(row.discount_cell.amount.gross_string, equals('0,00'));
            row = table.rows[1];
            expect(row.split_cell.amount.net_string, equals('16,81'));
            expect(row.split_cell.amount.tax_string, equals('3,19'));
            expect(row.split_cell.amount.gross_string, equals('20,00'));
            expect(row.discount_cell.amount.net_string, equals('0,00'));
            expect(row.discount_cell.amount.tax_string, equals('0,00'));
            expect(row.discount_cell.amount.gross_string, equals('0,00'));

        });

        test("auto_split() with 1% discount", () {

            amount_input.value = '500,00';
            discount_input.selectedIndex = 1;

            PaymentSplit row = table.rows.first;

            expect(row.split_cell.amount.net_string, equals('0,00'));
            expect(row.split_cell.amount.tax_string, equals('0,00'));
            expect(row.split_cell.amount.gross_string, equals('0,00'));

            table.auto_split();

            expect(row.split_cell.amount.net_string, equals('384,91'));
            expect(row.split_cell.amount.tax_string, equals('90,29'));
            expect(row.split_cell.amount.gross_string, equals('475,20'));
            expect(row.discount_cell.amount.net_string, equals('3,89'));
            expect(row.discount_cell.amount.tax_string, equals('0,91'));
            expect(row.discount_cell.amount.gross_string, equals('4,80'));
            row = table.rows[1];
            expect(row.split_cell.amount.net_string, equals('20,84'));
            expect(row.split_cell.amount.tax_string, equals('3,96'));
            expect(row.split_cell.amount.gross_string, equals('24,80'));
            expect(row.discount_cell.amount.net_string, equals('0,21'));
            expect(row.discount_cell.amount.tax_string, equals('0,04'));
            expect(row.discount_cell.amount.gross_string, equals('0,25'));

        });

        test("recalculate() totals", () {

            amount_input.value = '500,00';
            discount_input.selectedIndex = 1;
            table.auto_split();

            Amount payment_total = table.split_gross_total.amount;
            expect(payment_total.net_string, equals('405,75'));
            expect(payment_total.tax_string, equals('94,25'));
            expect(payment_total.gross_string, equals('500,00'));

            Amount discount_total = table.discount_gross_total.amount;
            expect(discount_total.net_string, equals('4,10'));
            expect(discount_total.tax_string, equals('0,95'));
            expect(discount_total.gross_string, equals('5,05'));

            Amount credit_total = table.credit_gross_total.amount;
            expect(credit_total.net_string, equals('409,85'));
            expect(credit_total.tax_string, equals('95,20'));
            expect(credit_total.gross_string, equals('505,05'));
        });

    });

}
