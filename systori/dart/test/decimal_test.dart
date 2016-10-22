import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:systori/decimal.dart';

main() async {

    group("currency parsing", () {

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

}