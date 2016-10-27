@TestOn('vm')
import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:systori/spreadsheet.dart';
import 'package:systori/decimal.dart';


main() async {

    group("ConvertEquation", () {

        canonical(String equation) =>
            ConvertEquation.localToCanonical(equation);

        local(String equation) =>
            ConvertEquation.canonicalToLocal(equation);

        test("convert de", () {
            Intl.withLocale("de", ()=> Decimal.updateFormats());

            expect(canonical("2-1 000,001"), "2 - 1000.001");
            expect(canonical("2-1.000,001"), "2 - 1000.001");
            expect(canonical("2--1.000,001"), "2 - -1000.001");
            expect(canonical("2--1.000,001+A!"), "(2 - -1000.001) + A!");

            expect(local("2 - 1000.001"), "2 - 1.000,001");
            expect(local("2 - -1000.001"), "2 - -1.000,001");

        });

        test("convert en", () {
            Intl.withLocale("en", ()=> Decimal.updateFormats());

            expect(canonical("2-1 000.001"), "2 - 1000.001");
            expect(canonical("2-1,000.001"), "2 - 1000.001");
            expect(canonical("2--1,000.001"), "2 - -1000.001");
            expect(canonical("2--1,000.001+A@1:&"), "(2 - -1000.001) + A@1:&");

            expect(local("2 - 1000.001"), "2 - 1,000.001");
            expect(local("2 - -1000.001"), "2 - -1,000.001");

        });

        tearDown(() {
            Intl.withLocale('en', ()=> Decimal.updateFormats());
        });

    });

    group("EvaluateEquation", () {

        solve(String equation) => EvaluateEquation.solve(equation);

        test("solve", () {
            expect(solve("-16/(5-3)").decimal, -8.0);
            expect(solve("-1+!3:&").decimal, 1.0);
            expect(solve(" 16.0 / (5-3) ").decimal, 8.0);
        });

        test("solve with negative numbers", () {
            expect(solve(" -16.0 / (5-3) ").decimal, -8.0);
            expect(solve(" 16.0 /  -1*(5-3) ").decimal, -32.0);
            expect(solve(" 16.0 / (-1*(5-3)) ").decimal, -8.0);
        });

    });
}