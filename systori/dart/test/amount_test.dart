import 'dart:html';
import 'package:intl/intl.dart';
import 'package:test/test.dart';
import '../web/amount_element.dart';

void main() {
    Intl.systemLocale = 'de';
    registerAmountElements();

    group("Amount", () {
        test("*_string attributes", () {
            Amount a = new Amount(100000, 19000, 0.19);
            expect(a.net_string, equals("1.000,00"));
            expect(a.tax_string, equals("190,00"));
            expect(a.gross_string, equals("1.190,00"));
        });
        test("update_gross()", () {
            Amount a = new Amount(0, 0, 0.19);
            a.gross = 23800;
            expect(a.net, equals(20000));
            expect(a.tax, equals(3800));
            expect(a.gross, equals(23800));
        });
        test("operator *", () {
            Amount a = new Amount(100, 19, 0.19);
            Amount a2 = a * 0.5;
            expect(a2.net, equals(50));
            expect(a2.tax, equals(10));
            expect(a2.gross, equals(60));
            expect(a2.tax_rate, equals(0.19));
        });
        test("operator -", () {
            Amount a = new Amount(100, 19, 0.19);
            Amount a2 = new Amount(10, 9, 0.19);
            Amount a3 = a - a2;
            expect(a3.net, equals(90));
            expect(a3.tax, equals(10));
            expect(a3.gross, equals(100));
            expect(a3.tax_rate, equals(0.19));
        });
        test("operator +", () {
            Amount a = new Amount(100, 19, 0.19);
            Amount a2 = new Amount(10, 9, 0.19);
            Amount a3 = a + a2;
            expect(a3.net, equals(110));
            expect(a3.tax, equals(28));
            expect(a3.gross, equals(138));
            expect(a3.tax_rate, equals(0.19));
        });
    });

    group("AmountViewCell", () {
        test("is registered", () {
            AmountViewCell cell = querySelector(".test-amount-view");
            expect(cell.amount_from_divs().gross, equals(48000));
            expect(cell.amount.gross_string, equals("480,00"));
        });
    });

    group("AmountInputCell", () {
        test("is registered", () {
            AmountInputCell cell = querySelector(".test-amount-input");
            expect(cell.amount_from_inputs().gross, equals(571200));
            expect(cell.amount.gross_string, equals("5.712,00"));
        });
    });
}
