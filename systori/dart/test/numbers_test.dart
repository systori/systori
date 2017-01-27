import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:systori/numbers.dart';

main() async {

    setLanguage(String lang) =>
        Intl.withLocale(lang, ()=> Decimal.updateFormats());

    group("Decimal.parse()", () {

        double to_double(String number) => new Decimal.parse(number).decimal;

        test("deutsch amounts", () {
            setLanguage('de');
            expect(to_double(''), null);
            expect(to_double('0'), 0.0);
            expect(to_double('1'), 1.0);
            expect(to_double('1,00'), 1.0);
            expect(to_double('1.000,00'), 1000.0);
            expect(to_double('1.2.3.4,00'), 1234.0);
        });

        test("english amounts", () {
            setLanguage('en');
            expect(to_double(''), null);
            expect(to_double('0'), 0.0);
            expect(to_double('1'), 1.0);
            expect(to_double('1.00'), 1.0);
            expect(to_double('1,000.00'), 1000.0);
            expect(to_double('1,2,3,4.00'), 1234.0);
        });

    });

    group("Amount", () {

        test("deutsch money formatting", () {
            setLanguage('de');
            Amount a = new Amount.from(1000, 190, 0.19);
            expect(a.net.money, "1.000,00");
            expect(a.tax.money, "190,00");
            expect(a.gross.money, "1.190,00");
        });

        test("english money formatting", () {
            setLanguage('en');
            Amount a = new Amount.from(1000, 190, 0.19);
            expect(a.net.money, "1,000.00");
            expect(a.tax.money, "190.00");
            expect(a.gross.money, "1,190.00");
        });

        test("english fromStrings()", () {
            setLanguage('en');
            var a = new Amount.fromStrings("1,000.00", "190.00", "0.19");
            expect(a.net.decimal, 1000.00);
            expect(a.tax.decimal, 190.00);
            expect(a.gross.decimal, 1190.00);
            expect(a.tax_rate.decimal, 0.19);
        });

        test("deutsch fromStrings()", () {
            setLanguage('de');
            var a = new Amount.fromStrings("1.000,00", "190,00", "0,19");
            expect(a.net.decimal, 1000.00);
            expect(a.tax.decimal, 190.00);
            expect(a.gross.decimal, 1190.00);
            expect(a.tax_rate.decimal, 0.19);
        });

        test("fromGross()", () {
            var a = new Amount.fromGross(new Decimal(238), new Decimal(0.19));
            expect(a.net.decimal, 200.00);
            expect(a.tax.decimal, 38.00);
            expect(a.gross.decimal, 238.00);
            expect(a.tax_rate.decimal, 0.19);
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

        test("operator ==", () {
            expect(new Amount.from(100, 19, 0.19) == new Amount.from(100, 19, 0.19), isTrue);
            expect(new Amount.from(101, 19, 0.19) == new Amount.from(100, 19, 0.19), isFalse);
            expect(new Amount.from(100, 20, 0.19) == new Amount.from(100, 19, 0.19), isFalse);
            expect(new Amount.from(100, 19, 0.2) == new Amount.from(100, 19, 0.19), isFalse);
            expect(new Amount.from(100, 19, 0.19) == new Decimal(119), isFalse);
            expect(new Amount.fromGross(new Decimal(119), new Decimal(0.19)) == new Amount.from(100, 19, 0.19), isTrue);
            expect(new Amount.from(100, 19, 0.19) == new Amount.fromGross(new Decimal(119), new Decimal(0.19)), isTrue);
        });

    });
}