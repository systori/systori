@TestOn('vm')
import 'package:test/test.dart';
import 'package:mockito/mockito_no_mirrors.dart';
import 'package:quiver/iterables.dart';
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
    TestCell(_value, [canonical="", _col=0, _row=0])
    {value=_value; this.canonical=canonical; this.column=_col; row=_row;}
}


List<Range> ranges(String eq) {
    var te = new TestEquation(eq);
    te.resolver = new RangeResolver();
    te.focused();
    te.calculate((i)=>[new TestCell(new Decimal(99))], true);
    return te.resolver.ranges;
}

Range extract(String eq) => ranges(eq).first;

List<Cell> column(List<int> ints, eq1, eq2) =>
    enumerate(ints).map((total) =>
    new TestCell(new Decimal(total.value),
        eq1==total.index||eq2==total.index ? '!' : '')
    ).toList();

Range range(String eq, List<int> ints, [eq1=-1, eq2=-1]) =>
    extract(eq)..calculate(column(ints, eq1, eq2));

double total(String eq, List<int> ints, [eq1=-1, eq2=-1]) =>
    extract(eq).calculate(column(ints, eq1, eq2)).decimal;

List index(String eq, List<int> ints, [eq1=-1, eq2=-1]) {
    var _range = range(eq, ints, eq1, eq2);
    return [_range.result.start, _range.result.end];
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

            e.focused();
            expect(e.local, "-1,000 + !:");
            expect(e.resolved, isNull);
            expect(e.value.decimal, 98);

            e.calculate((i)=>[new TestCell(new Decimal(99))], true);
            expect(e.local, "-1,000 + !:");
            expect(e.resolved, "-1,000  + 99");
            expect(e.value.decimal, -901);
        });

    });

    group("Range parsing", () {

        test("ranges", () {
            expect(ranges('1+1').length, 0);
            expect(ranges('(1+1)-A@7').length, 1);
            expect(ranges('(1+!&*(1/!))-A@7').length, 3);
        });

        test("column", () {
            expect(extract('@').column, null);
            expect(extract('A@').column, 0);
            expect(extract('C@').column, 2);
        });

        test("start/isStartEquation", () {
            expect(extract('@').start, 1);
            expect(extract('@4').start, 4);
            expect(extract('@99:').start, 99);
            expect(extract('@').isStartEquation, false);
            expect(extract('@&').isStartEquation, true);
        });

        test("end/isEndEquation", () {
            expect(extract('@').end, null);
            expect(extract('@4:').end, null);
            expect(extract('@9:9').end, 9);
            expect(extract('@').isEndEquation, false);
            expect(extract('@:&').isEndEquation, true);
        });

    });

    group("Range.calculate()", () {

        test("top-down summing, specific row", () {
            expect(total('@', [1, 2, 4]), 1);
            expect(total('@1', [1, 2, 4]), 1);
            expect(total('@3', [1, 2, 4]), 4);
        });

        test("bottom-up summing, specific row", () {
            expect(total('!', [1, 2, 4]), 4);
            expect(total('!1', [1, 2, 4]), 4);
            expect(total('!3', [1, 2, 4]), 1);
        });

        test("top-down summing, simple ranges", () {
            expect(total('@:', [1, 2, 4]), 7);
            expect(total('@1:', [1, 2, 4]), 7);
            expect(total('@1:1', [1, 2, 4]), 1);
            expect(total('@1:3', [1, 2, 4]), 7);
            expect(total('@2:3', [1, 2, 4]), 6);
        });

        test("bottom-up summing, simple ranges", () {
            expect(total('!:', [1, 2, 4]), 7);
            expect(total('!1:', [1, 2, 4]), 7);
            expect(total('!1:1', [1, 2, 4]), 4);
            expect(total('!1:3', [1, 2, 4]), 7);
            expect(total('!2:3', [1, 2, 4]), 3);
        });

        test("top-down summing, exclusive ranges", () {
            expect(total('@]', [1, 2, 4, 5]), 7);
            expect(total('@[', [1, 2, 4, 5]), 11);
            expect(total('@[]', [1, 2, 4, 5]), 6);
            expect(total('@2[', [1, 2, 4, 5]), 9);
            expect(total('@]3', [1, 2, 4, 5]), 3);
        });

        test("bottom-up summing, exclusive ranges", () {
            expect(total('!]', [1, 2, 4, 5]), 11);
            expect(total('![', [1, 2, 4, 5]), 7);
            expect(total('![]', [1, 2, 4, 5]), 6);
            expect(total('!2[', [1, 2, 4, 5]), 3);
            expect(total('!]3', [1, 2, 4, 5]), 9);
        });

        test("top-down summing, equation stops, simple", () {
            expect(total('@&', [1, 2, 4, 5]), 0);
            expect(total('@&', [1, 2, 4, 5], 0), 1);
            expect(total('@&', [1, 2, 4, 5], 3), 5);
        });

        test("bottom-up summing, equation stops, simple", () {
            expect(total('!&', [1, 2, 4, 5]), 0);
            expect(total('!&', [1, 2, 4, 5], 0), 1);
            expect(total('!&', [1, 2, 4, 5], 3), 5);
        });

        test("top-down summing, specific equation stops, simple", () {
            expect(total('@&', [1, 2, 4, 5], 1, 3), 2);
            expect(total('@&1', [1, 2, 4, 5], 1, 3), 2);
            expect(total('@&2', [1, 2, 4, 5], 1, 3), 5);
        });

        test("bottom-up summing, specific equation stops, simple", () {
            expect(total('!&', [1, 2, 4, 5], 1, 3), 5);
            expect(total('!&1', [1, 2, 4, 5], 1, 3), 5);
            expect(total('!&2', [1, 2, 4, 5], 1, 3), 2);
        });

        test("top-down summing, equation stops, range", () {
            expect(total('@&:', [1, 2, 4, 5]), 0);
            expect(total('@&:', [1, 2, 4, 5], 0), 12);
            expect(total('@&:', [1, 2, 4, 5], 2), 9);
            expect(total('@:&', [1, 2, 4, 5], 2), 7);
            expect(total('@]&', [1, 2, 4, 5], 2), 3);
            expect(total('@1:]&', [1, 2, 4, 5], 2), 3);
        });

        test("bottom-up summing, equation stops, range", () {
            expect(total('!&:', [1, 2, 4, 5]), 0);
            expect(total('!:&', [1, 2, 4, 5]), 0);
            expect(total('!&:&', [1, 2, 4, 5]), 0);
            expect(total('!&:', [1, 2, 4, 5], 3), 12);
            expect(total('!&:', [1, 2, 4, 5], 2), 7);
            expect(total('!:&', [1, 2, 4, 5], 2), 9);
            expect(total('!]&', [1, 2, 4, 5], 2), 5);
            expect(total('!1:]&', [1, 2, 4, 5], 2), 5);
        });

        test("top-down summing, specific equation stops, range", () {
            expect(total('@&:&2', [1, 2, 4, 5], 1, 3), 11);
            expect(total('@&2:', [1, 2, 4, 5], 0, 2), 9);
        });

        test("bottom-up summing, specific equation stops, range", () {
            expect(total('!&:&2', [1, 2, 4, 5], 1, 3), 11);
            expect(total('!&2:', [1, 2, 4, 5], 1, 2), 3);
        });

    });

    group("RangeResult.start/end", () {

        test("top-down, no range", () {
            expect(index('@', [1, 2, 4]), [0, 0]);
            expect(index('@1', [1, 2, 4]), [0, 0]);
            expect(index('@3', [1, 2, 4]), [2, 2]);
        });

        test("top-down, with range", () {
            expect(index('@:3', [1, 2, 4]), [0, 2]);
            expect(index('@:1', [1, 2, 4]), [0, 0]);
            expect(index('@1:', [1, 2, 4]), [0, 2]);
            expect(index('@3:', [1, 2, 4]), [2, 2]);
            expect(index('@2:', [1, 2, 4]), [1, 2]);
        });

        test("bottom-up, no range", () {
            expect(index('!', [1, 2, 4]), [2, 2]);
            expect(index('!1', [1, 2, 4]), [2, 2]);
            expect(index('!3', [1, 2, 4]), [0, 0]);
        });

        test("bottom-up, with range", () {
            expect(index('!:3', [1, 2, 4]), [0, 2]);
            expect(index('!:1', [1, 2, 4]), [2, 2]);
            expect(index('!1:', [1, 2, 4]), [0, 2]);
            expect(index('!3:', [1, 2, 4]), [0, 0]);
            expect(index('!2:', [1, 2, 4]), [0, 1]);
        });
    });

    group("RangeResult.start/end for '&'", () {

        test("equation stops, no matches", () {
            expect(index('!&:',  [1, 2, 4, 5]), [-1, -1]);
            expect(index('!:&',  [1, 2, 4, 5]), [-1, -1]);
            expect(index('!&:&', [1, 2, 4, 5]), [-1, -1]);
            expect(index('!3:&',   [1, 2, 4, 5], 2, 3), [-1, -1]);
            expect(index('@&:',  [1, 2, 4, 5]), [-1, -1]);
            expect(index('@:&',  [1, 2, 4, 5]), [-1, -1]);
            expect(index('@&:&', [1, 2, 4, 5]), [-1, -1]);
            expect(index('@3:&',   [1, 2, 4, 5], 0, 1), [-1, -1]);
        });

        test("equation stops, with matches", () {
            expect(index('!&',   [1, 2, 4, 5], 1, 3), [3, 3]);
            expect(index('!&:&', [1, 2, 4, 5], 1, 3), [3, 3]);
            expect(index('!2:&', [1, 2, 4, 5], 0), [0, 2]);
            expect(index('!&:3', [1, 2, 4, 5], 3), [1, 3]);
            expect(index('@&',   [1, 2, 4, 5], 1, 3), [1, 1]);
            expect(index('@&:&', [1, 2, 4, 5], 1, 3), [1, 1]);
            expect(index('@2:&', [1, 2, 4, 5], 2), [1, 2]);
            expect(index('@&:3', [1, 2, 4, 5], 1), [1, 2]);
        });

    });

}