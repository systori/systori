import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:systori/decimal.dart';

main() async {

    group("Decimal.parse()", () {

        double to_double(String number) => new Decimal.parse(number).decimal;

        test("german amounts", () {
            Intl.withLocale('de', ()=> Decimal.updateFormats());
            expect(to_double(''), null);
            expect(to_double('0'), 0.0);
            expect(to_double('1'), 1.0);
            expect(to_double('1,00'), 1.0);
            expect(to_double('1.000,00'), 1000.0);
            expect(to_double('1.2.3.4,00'), 1234.0);
        });

        test("american amounts", () {
            Intl.withLocale('en', ()=> Decimal.updateFormats());
            expect(to_double(''), null);
            expect(to_double('0'), 0.0);
            expect(to_double('1'), 1.0);
            expect(to_double('1.00'), 1.0);
            expect(to_double('1,000.00'), 1000.0);
            expect(to_double('1,2,3,4.00'), 1234.0);
        });

        tearDown(() {
            Intl.withLocale('en', ()=> Decimal.updateFormats());
        });

    });

}