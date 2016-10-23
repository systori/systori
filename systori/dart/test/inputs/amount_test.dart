@TestOn('browser')
import 'dart:html';
import 'package:intl/intl.dart';
import 'package:test/test.dart';
import 'package:systori/decimal.dart';
import 'package:systori/src/inputs/amount.dart';

void main() {
    Intl.systemLocale = 'de';
    registerAmountElements();

    var tax_rate = new Decimal(0.19);

    group("Amount", () {
        test("decimal.money attribute", () {
            Amount a = new Amount.from(1000, 190, 0.19);
            expect(a.net.money, "1.000,00");
            expect(a.tax.money, "190,00");
            expect(a.gross.money, "1.190,00");
        });
        test("updateGross()", () {
            var a = new Amount.fromGross(new Decimal(238), tax_rate);
            expect(a.net.decimal, 200.00);
            expect(a.tax.decimal, 38.00);
            expect(a.gross.decimal, 238.00);
        });
        test("operator *", () {
            Amount a = new Amount.from(100, 19, 0.19);
            Amount a2 = a * new Decimal(0.5);
            expect(a2.net.decimal, 50);
            expect(a2.tax.decimal, 9.5);
            expect(a2.gross.decimal, 59.5);
            expect(a2.tax_rate.decimal, 0.19);
        });
        test("operator -", () {
            Amount a = new Amount.from(100, 19, 0.19);
            Amount a2 = new Amount.from(10, 9, 0.19);
            Amount a3 = a - a2;
            expect(a3.net.decimal, 90);
            expect(a3.tax.decimal, 10);
            expect(a3.gross.decimal, 100);
            expect(a3.tax_rate.decimal, 0.19);
        });
        test("operator +", () {
            Amount a = new Amount.from(100, 19, 0.19);
            Amount a2 = new Amount.from(10, 9, 0.19);
            Amount a3 = a + a2;
            expect(a3.net.decimal, 110);
            expect(a3.tax.decimal, 28);
            expect(a3.gross.decimal, 138);
            expect(a3.tax_rate.decimal, 0.19);
        });
    });

    group("AmountViewCell", () {
        test("is registered", () {
            AmountViewCell cell = querySelector(".test-amount-view");
            expect(cell.amountFromViews().gross.decimal, 480);
            expect(cell.amount.gross.money, "480,00");
        });
    });

    group("AmountInputCell", () {
        test("is registered", () {
            AmountInputCell cell = querySelector(".test-amount-input");
            expect(cell.amountFromInputs().gross.decimal, 5712);
            expect(cell.amount.gross.money, "5.712,00");
        });
    });
}
