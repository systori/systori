import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:systori/decimal.dart';

main() async {

    group("Decimal.parse()", () {

        double to_double(String number) => new Decimal.parse(number).decimal;

        test("german amounts", () {
            Intl.withLocale('de', ()=> Decimal.updateFormats());
            expect(to_double(''), equals(null));
            expect(to_double('0'), equals(0.0));
            expect(to_double('1'), equals(1.0));
            expect(to_double('1,00'), equals(1.0));
            expect(to_double('1.000,00'), equals(1000.0));
        });

        test("american amounts", () {
            Intl.withLocale('en', ()=> Decimal.updateFormats());
            expect(to_double(''), equals(null));
            expect(to_double('0'), equals(0.0));
            expect(to_double('1'), equals(1.0));
            expect(to_double('1.00'), equals(1.0));
            expect(to_double('1,000.00'), equals(1000.0));
        });

        tearDown(() {
            Intl.withLocale('en', ()=> Decimal.updateFormats());
        });

    });

    group("Decimal.isNullBlankOrNumber", () {

        bool isNBON(String txt) => Decimal.isNullBlankOrNumber(txt);

        test("true", () {
            expect(isNBON(''), true);
            expect(isNBON('0'), true);
            expect(isNBON('1'), true);
            expect(isNBON('  '), true);
            expect(isNBON(null), true);
            expect(isNBON('1,00 '), true);
            expect(isNBON(' 1.000,00'), true);
            expect(isNBON(' -1.000,00'), true);
        });

        test("false", () {
            expect(isNBON('A'), false);
            expect(isNBON('1 2'), false);
            expect(isNBON('1%'), false);
            expect(isNBON('1-2'), false);
            expect(isNBON('(1.000,00)'), false);
        });

    });
}