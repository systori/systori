@TestOn('vm')
import 'package:test/test.dart';
import 'package:mockito/mockito_no_mirrors.dart';
import 'package:intl/intl.dart';
import 'package:systori/spreadsheet.dart';
import 'package:systori/decimal.dart';


class MockRangeResolver extends Mock implements RangeResolver {}

class TestEquation extends Equation {
    String canonical, local, resolved;
    TestEquation([this.canonical="", value]) {
        if (value != null) this.value = value;
        resolver = new MockRangeResolver();
        when(resolver.resolve(
            typed(any), typed(any), typed(any), typed(any), typed(any), typed(any),
            typed(any), typed(any), typed(any), typed(any), typed(any), typed(any)))
        .thenReturn(new Decimal(99));
    }
}


class TestCell extends Cell {
    String canonical, local, resolved;
    Cell(_value, [canonical="", _col=0, _row=0])
    {value=_value; column=_col; row=_row;}
}


main() async {

    group("ConvertEquation", () {

        canonical(String equation) =>
            new TestEquation().localToCanonical(equation);

        local(String equation) =>
            new TestEquation().canonicalToLocal(equation);

        resolve(String equation) =>
            new TestEquation().localToResolved(equation);

        test("convert de", () {
            Intl.withLocale("de", ()=> Decimal.updateFormats());

            expect(canonical("2-1 000,001"), "2 - 1000.001");
            expect(canonical("2-1.000,001"), "2 - 1000.001");
            expect(canonical("2--1.000,001"), "2 - -1000.001");
            expect(canonical("2--1.000,001+A!"), "(2 - -1000.001) + A!");

            expect(local("2 - 1000.001"), "2 - 1.000,001");
            expect(local("2 - -1000.001"), "2 - -1.000,001");

            expect(resolve("2--1.000,001+A!"), "(2 - -1.000,001) + 99");
        });

        test("convert en", () {
            Intl.withLocale("en", ()=> Decimal.updateFormats());

            expect(canonical("2-1 000.001"), "2 - 1000.001");
            expect(canonical("2-1,000.001"), "2 - 1000.001");
            expect(canonical("2--1,000.001"), "2 - -1000.001");
            expect(canonical("2--1,000.001+A@1:&"), "(2 - -1000.001) + A@1:&");

            expect(local("2 - 1000.001"), "2 - 1,000.001");
            expect(local("2 - -1000.001"), "2 - -1,000.001");

            expect(resolve("2--1,000.001+A@1:&"), "(2 - -1,000.001) + 99");
        });

        tearDown(() {
            Intl.withLocale('en', ()=> Decimal.updateFormats());
        });

    });

    group("EvaluateEquation", () {

        solve(String equation) => new TestEquation().eval(equation);

        test("solve", () {
            expect(solve("-16/(5-3)").decimal, -8.0);
            expect(solve("-1+!3:&").decimal, 98.0);
            expect(solve(" 16.0 / (5-3) ").decimal, 8.0);
        });

        test("solve with negative numbers", () {
            expect(solve(" -16.0 / (5-3) ").decimal, -8.0);
            expect(solve(" 16.0 /  -1*(5-3) ").decimal, -32.0);
            expect(solve(" 16.0 / (-1*(5-3)) ").decimal, -8.0);
        });

    });

    group("Equation", () {

        test("solve", () {
            var e = new TestEquation("-1000.00+!:", new Decimal(98.0));
            e.resolver = new RangeResolver();

            expect(e.local, isNull);
            expect(e.resolved, isNull);
            expect(e.value.decimal, 98);

            e.focus();
            expect(e.local, "-1,000 + !:");
            expect(e.resolved, isNull);
            expect(e.value.decimal, 98);

            e.calculate((i)=>[new TestCell()..value=new Decimal(99)], true);
            expect(e.local, "-1,000 + !:");
            expect(e.resolved, "-1,000  + 99");
            expect(e.value.decimal, -901);
        });

    });

}