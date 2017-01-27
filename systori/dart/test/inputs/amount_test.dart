@TestOn('browser')
import 'dart:html';
import 'package:intl/intl.dart';
import 'package:test/test.dart';
import 'package:systori/inputs.dart';
import 'package:systori/numbers.dart';
import '../scaffolding.dart';


void main() {
    Intl.systemLocale = 'de';
    registerAmountElements();

    Scaffolding scaffold = new Scaffolding(querySelector('#scaffold'));

    setUp(() {
        scaffold.reset();
    });

    group("AmountViewCell", () {

        AmountViewCell cell;

        setUp(() {
            cell = querySelector(".test-amount-view");
        });

        test("amountFromViews", () {
            expect(cell.amount.gross.money, "480,00");
            expect(cell.amount.net.money, "388,80");
            expect(cell.amount.tax.money, "91,20");
        });

        test("update", () {
            cell.update(new Amount.from(100, 19, 0.19));
            expect(cell.querySelector(':scope>.amount-gross>.amount-value').text, "119,00");
            expect(cell.querySelector(':scope>.amount-net>.amount-value').text, "100,00");
            expect(cell.querySelector(':scope>.amount-tax>.amount-value').text, "19,00");
        });

    });

    group("AmountInputCell", () {

        AmountInputCell cell;
        InputElement gross;
        InputElement net;
        InputElement tax;

        setUp(() {
            cell = querySelector(".test-amount-input");
            gross = cell.querySelector(':scope>.amount-gross');
            net = cell.querySelector(':scope>.amount-net');
            tax = cell.querySelector(':scope>.amount-tax');
        });

        test("amountFromInputs", () {
            expect(cell.amount.gross.money, "5.712,00");
            expect(cell.amount.net.money, "4.800,00");
            expect(cell.amount.tax.money, "912,00");
        });

        test("update", () {
            cell.update(new Amount.from(100, 19, 0.19));
            expect(gross.value, "119,00");
            expect(net.value, "100,00");
            expect(tax.value, "19,00");
        });

        test("grossChanged", () {
            gross.value = '119,00';
            cell.grossChanged();
            expect(cell.amount.gross.money, "119,00");
            expect(cell.amount.net.money, "100,00");
            expect(cell.amount.tax.money, "19,00");
        });

        test("netChanged", () {
            net.value = '5000,00';
            cell.netChanged();
            expect(cell.amount.gross.money, "5.712,00");
            expect(cell.amount.net.money, "5.000,00");
            expect(cell.amount.tax.money, "712,00");
        });

        test("taxChanged", () {
            tax.value = '1000,00';
            cell.taxChanged();
            expect(cell.amount.gross.money, "5.712,00");
            expect(cell.amount.net.money, "4.712,00");
            expect(cell.amount.tax.money, "1.000,00");
        });

    });
}
