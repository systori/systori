@TestOn('vm')
import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';


class TestCell extends Cell {
    String canonical, local, resolved, preview;
    TestCell(_canonical, _value, [_col=0, _row=0])
    {this.canonical=_canonical; this.value=new Decimal(_value); this.column=_col; row=_row;}
}


// Cell helpers

Cell cell([String txt='', num value=0, _col=0, _row=0]) =>
    new TestCell(txt, value, _col, _row);

List<Cell> cells(List<int> ints, [eq1=-1, eq2=-1]) =>
    enumerate(ints).
    map((total) => cell(eq1==total.index||eq2==total.index ? '!' : '', total.value)).
    toList();

ColumnGetter columnGetterReturns(List<int> ints, [eq1=-1, eq2=-1]) =>
    (col) => cells(ints, eq1, eq2);

Cell eval(String eq, List<int> ints, [eq1=-1, eq2=-1]) =>
    cell(eq, 0, 0, ints.length)..calculate(columnGetterReturns(ints, eq1, eq2), dependenciesChanged: true);

double cellTotal(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    eval(eq, ints!=null?ints:[], eq1, eq2).value.decimal;

// Range helpers

List<Range> ranges(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    eval(eq, ints!=null?ints:[], eq1, eq2).resolver.ranges;

Range range(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    ranges(eq, ints, eq1, eq2).first;

List index(String eq, List<int> ints, [eq1=-1, eq2=-1]) {
    var _range = range(eq, ints, eq1, eq2);
    return [_range.result.start, _range.result.end];
}

double rangeTotal(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    range(eq, ints, eq1, eq2).result.value.decimal;


main() async {

    group("Conversion", () {

        canonical(String equation) => cell().localToCanonical(equation);
        local(String equation) => cell().canonicalToLocal(equation);
        resolve(String equation, List<int> ints) =>
            (cell('', 0, 0, ints.length)..resolver.getColumn = columnGetterReturns(ints))
            .localToResolved(equation);

        test("locale: de", () {
            Intl.withLocale("de", ()=> Decimal.updateFormats());

            expect(canonical("2-1 000,001"), "2 - 1000.001");
            expect(canonical("2-1.000,001"), "2 - 1000.001");
            expect(canonical("2--1.000,001"), "2 - -1000.001");
            expect(canonical("2--1.000,001+A!"), "(2 - -1000.001) + A!");

            expect(local("2 - 1000.001"), "2 - 1.000,001");
            expect(local("2 - -1000.001"), "2 - -1.000,001");

            expect(resolve("2--1.000,001+A!", [99]), "(2 - -1.000,001) + 99");
        });

        test("locale: en", () {
            Intl.withLocale("en", ()=> Decimal.updateFormats());

            expect(canonical("2-1 000.001"), "2 - 1000.001");
            expect(canonical("2-1,000.001"), "2 - 1000.001");
            expect(canonical("2--1,000.001"), "2 - -1000.001");
            expect(canonical("2--1,000.001+A@1:&"), "(2 - -1000.001) + A@1:&");

            expect(local("2 - 1000.001"), "2 - 1,000.001");
            expect(local("2 - -1000.001"), "2 - -1,000.001");

            expect(resolve("2--1,000.001+A@1:", [99]), "(2 - -1,000.001) + 99");
        });

        tearDown(() {
            Intl.withLocale('en', ()=> Decimal.updateFormats());
        });

    });

    group("Range parsing", () {

        test("many ranges", () {
            expect(ranges('1+1').length, 0);
            expect(ranges('(1+1)-A@7').length, 1);
            expect(ranges('(1+!&*(1/!))-A@7', [1]).length, 3);
        });

        test("column", () {
            expect(range('@').column, null);
            expect(range('A@').column, 0);
            expect(range('C@').column, 2);
        });

        test("start/isStartEquation", () {
            expect(range('@').start, 1);
            expect(range('@4').start, 4);
            expect(range('@99:').start, 99);
            expect(range('@').isStartEquation, false);
            expect(range('@&').isStartEquation, true);
        });

        test("end/isEndEquation", () {
            expect(range('@').end, null);
            expect(range('@4:').end, null);
            expect(range('@9:9').end, 9);
            expect(range('@').isEndEquation, false);
            expect(range('@:&').isEndEquation, true);
        });

    });

    group("Range.calculate()", () {

        test("top-down summing, specific row", () {
            expect(rangeTotal('@', [1, 2, 4]), 1);
            expect(rangeTotal('@1', [1, 2, 4]), 1);
            expect(rangeTotal('@3', [1, 2, 4]), 4);
        });

        test("bottom-up summing, specific row", () {
            expect(rangeTotal('!', [1, 2, 4]), 4);
            expect(rangeTotal('!1', [1, 2, 4]), 4);
            expect(rangeTotal('!3', [1, 2, 4]), 1);
        });

        test("top-down summing, simple ranges", () {
            expect(rangeTotal('@:', [1, 2, 4]), 7);
            expect(rangeTotal('@1:', [1, 2, 4]), 7);
            expect(rangeTotal('@1:1', [1, 2, 4]), 1);
            expect(rangeTotal('@1:3', [1, 2, 4]), 7);
            expect(rangeTotal('@2:3', [1, 2, 4]), 6);
        });

        test("bottom-up summing, simple ranges", () {
            expect(rangeTotal('!:', [1, 2, 4]), 7);
            expect(rangeTotal('!1:', [1, 2, 4]), 7);
            expect(rangeTotal('!1:1', [1, 2, 4]), 4);
            expect(rangeTotal('!1:3', [1, 2, 4]), 7);
            expect(rangeTotal('!2:3', [1, 2, 4]), 3);
        });

        test("top-down summing, exclusive ranges", () {
            expect(rangeTotal('@]', [1, 2, 4, 5]), 7);
            expect(rangeTotal('@[', [1, 2, 4, 5]), 11);
            expect(rangeTotal('@[]', [1, 2, 4, 5]), 6);
            expect(rangeTotal('@2[', [1, 2, 4, 5]), 9);
            expect(rangeTotal('@]3', [1, 2, 4, 5]), 3);
        });

        test("bottom-up summing, exclusive ranges", () {
            expect(rangeTotal('!]', [1, 2, 4, 5]), 11);
            expect(rangeTotal('![', [1, 2, 4, 5]), 7);
            expect(rangeTotal('![]', [1, 2, 4, 5]), 6);
            expect(rangeTotal('!2[', [1, 2, 4, 5]), 3);
            expect(rangeTotal('!]3', [1, 2, 4, 5]), 9);
        });

        test("top-down summing, equation stops, simple", () {
            expect(rangeTotal('@&', [1, 2, 4, 5]), 0);
            expect(rangeTotal('@&', [1, 2, 4, 5], 0), 1);
            expect(rangeTotal('@&', [1, 2, 4, 5], 3), 5);
        });

        test("bottom-up summing, equation stops, simple", () {
            expect(rangeTotal('!&', [1, 2, 4, 5]), 0);
            expect(rangeTotal('!&', [1, 2, 4, 5], 0), 1);
            expect(rangeTotal('!&', [1, 2, 4, 5], 3), 5);
        });

        test("top-down summing, specific equation stops, simple", () {
            expect(rangeTotal('@&', [1, 2, 4, 5], 1, 3), 2);
            expect(rangeTotal('@&1', [1, 2, 4, 5], 1, 3), 2);
            expect(rangeTotal('@&2', [1, 2, 4, 5], 1, 3), 5);
        });

        test("bottom-up summing, specific equation stops, simple", () {
            expect(rangeTotal('!&', [1, 2, 4, 5], 1, 3), 5);
            expect(rangeTotal('!&1', [1, 2, 4, 5], 1, 3), 5);
            expect(rangeTotal('!&2', [1, 2, 4, 5], 1, 3), 2);
        });

        test("top-down summing, equation stops, range", () {
            expect(rangeTotal('@&:', [1, 2, 4, 5]), 0);
            expect(rangeTotal('@&:', [1, 2, 4, 5], 0), 12);
            expect(rangeTotal('@&:', [1, 2, 4, 5], 2), 9);
            expect(rangeTotal('@:&', [1, 2, 4, 5], 2), 7);
            expect(rangeTotal('@]&', [1, 2, 4, 5], 2), 3);
            expect(rangeTotal('@1:]&', [1, 2, 4, 5], 2), 3);
        });

        test("bottom-up summing, equation stops, range", () {
            expect(rangeTotal('!&:', [1, 2, 4, 5]), 0);
            expect(rangeTotal('!:&', [1, 2, 4, 5]), 0);
            expect(rangeTotal('!&:&', [1, 2, 4, 5]), 0);
            expect(rangeTotal('!&:', [1, 2, 4, 5], 3), 12);
            expect(rangeTotal('!&:', [1, 2, 4, 5], 2), 7);
            expect(rangeTotal('!:&', [1, 2, 4, 5], 2), 9);
            expect(rangeTotal('!]&', [1, 2, 4, 5], 2), 5);
            expect(rangeTotal('!1:]&', [1, 2, 4, 5], 2), 5);
        });

        test("top-down summing, specific equation stops, range", () {
            expect(rangeTotal('@&:&2', [1, 2, 4, 5], 1, 3), 11);
            expect(rangeTotal('@&2:', [1, 2, 4, 5], 0, 2), 9);
        });

        test("bottom-up summing, specific equation stops, range", () {
            expect(rangeTotal('!&:&2', [1, 2, 4, 5], 1, 3), 11);
            expect(rangeTotal('!&2:', [1, 2, 4, 5], 1, 2), 3);
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

    group("Cell attributes", () {

        test("isBlank", () {
            expect(cell('').isCanonicalBlank, isTrue);
            expect(cell('0').isCanonicalBlank, isTrue);
            expect(cell('-0.0').isCanonicalBlank, isTrue);
            expect(cell('-0.1').isCanonicalBlank, isFalse);
        });

        test("isNumber", () {
            expect(cell('').isCanonicalNumber, isFalse);
            expect(cell('0').isCanonicalNumber, isTrue);
            expect(cell('-0.0').isCanonicalNumber, isTrue);
            expect(cell('-0.1').isCanonicalNumber, isTrue);
        });

        test("isEquation", () {
            expect(cell('').isCanonicalEquation, isFalse);
            expect(cell('0').isCanonicalEquation, isFalse);
            expect(cell('1,0.0').isCanonicalEquation, isFalse);
            expect(cell('-10').isCanonicalEquation, isFalse);
            expect(cell('1+1').isCanonicalEquation, isTrue);
            expect(cell('A').isCanonicalEquation, isTrue);
            expect(cell('!:').isCanonicalEquation, isTrue);
            expect(cell('!+!+!').isCanonicalEquation, isTrue);
        });

        test("isEquationChanged", () {
            var c = cell('');
            c.local = '';
            c.calculate((i)=>[]);
            expect(c.isLocalChanged, isFalse);

            c.local = '@';
            expect(c.isLocalChanged, isTrue);

            c.calculate((i)=>[]);
            expect(c.isLocalChanged, isFalse);

            c.local = '@';
            expect(c.isLocalChanged, isFalse);
            c.local = '!';
            expect(c.isLocalChanged, isTrue);
        });

        test("isPositionChanged", () {
            var c = cell('');
            c.row = 1;
            c.calculate((i)=>[]);
            expect(c.isPositionChanged, isFalse);

            c.row = 9;
            expect(c.isPositionChanged, isTrue);

            c.calculate((i)=>[]);
            expect(c.isPositionChanged, isFalse);

            c.row = 10;
            expect(c.isPositionChanged, isTrue);
        });

    });

    group("Cell.calculate(): value", () {

        test("single number ranges", () {
            expect(cellTotal('!+!+!', [1,2]), 6);
            expect(cellTotal('!2+!2+!2', [1,2]), 3);
            expect(cellTotal('@+@+@', [1,2]), 3);
            expect(cellTotal('@2+@2+@2', [1,2]), 6);
        });

        test("ranges, bottom-up", () {
            expect(cellTotal('!2:4+!5:', [1,2,3,4,5,6]), 15);
            expect(cellTotal('!:3+!5:', [1,2,3,4,5,6]), 18);
            expect(cellTotal('!:2+!4', [1,2,3,4,5,6]), 14);
        });

        test("ranges, top-down", () {
            expect(cellTotal('@2:4+@5:', [1,2,3,4,5,6]), 20);
            expect(cellTotal('@:3+@5:', [1,2,3,4,5,6]), 17);
            expect(cellTotal('@:2+@4', [1,2,3,4,5,6]), 7);
        });

        test("ranges, mixed", () {
            expect(cellTotal('@:2+!:2', [1,2,3,4,5,6]), 14);
            expect(cellTotal('@:3+!:3', [1,2,3,4,5,6]), 21);
            expect(cellTotal('@:+!:', [1,2,3,4,5,6]), 42);
        });

        test("solve with negative numbers", () {
            expect(cellTotal("-16/(5-3)"), -8.0);
            expect(cellTotal("-1+!2:&", [4,1,2,3], 1), 2);
            expect(cellTotal(" -16.0 / (5-3) "), -8.0);
            expect(cellTotal(" 16.0 /  -1*(5-3) "), -32.0);
            expect(cellTotal(" 16.0 / (-1*(5-3)) "), -8.0);
        });

    });

    group("Cell.calculate(): phases", () {

        test("isNumber && dependenciesChanged", () {

            var c = new TestCell("-1000.00", 0);
            var results = identityHashCode(c.resolver.results);

            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 0);

            // nothing happens for numbers
            c.calculate((i)=>[], dependenciesChanged: true);

            // after calculation
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 0);
            // results map was not reset
            expect(identityHashCode(c.resolver.results), results);

        });

        test("isEquation && dependenciesChanged", () {

            var c = new TestCell("2+2", 0);
            var results = identityHashCode(c.resolver.results);

            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 0);

            c.calculate((i)=>[], dependenciesChanged: true);

            expect(c.local, '');
            expect(c.resolved, '');
            expect(c.value.decimal, 4);
            // results map should have been reset
            expect(identityHashCode(c.resolver.results), isNot(results));

        });

        test("isNumber && focused", () {
            // nothing happens for focused numbers

            var c = new TestCell("-1000.00", 0);
            var results = identityHashCode(c.resolver.results);

            expect(c.canonical, "-1000.00");
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 0);

            c.calculate((i)=>[], focused: true);

            expect(c.canonical, "-1000.00");
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 0);
            expect(identityHashCode(c.resolver.results), results);

        });

        test("isEquation && focused", () {

            var c = new TestCell("(2 + 2000) + !", 0);
            var results = identityHashCode(c.resolver.results);

            expect(c.canonical, "(2 + 2000) + !");
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 0);

            c.calculate(columnGetterReturns([18]), focused: true);

            expect(c.canonical, "(2 + 2000) + !");
            expect(c.local, "(2 + 2,000) + !");
            expect(c.resolved, "(2  + 2,000) + 18");
            expect(c.value.decimal, 0);
            expect(identityHashCode(c.resolver.results), results);

        });

        test("isNumber && changed", () {

            var c = new TestCell("-1000.00", 0);
            var results = identityHashCode(c.resolver.results);

            expect(c.canonical, "-1000.00");
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 0);

            c.local = "9,999.00";
            c.calculate((i)=>[], changed: true);

            expect(c.canonical, "9999");
            expect(c.local, "9,999.00");
            expect(c.resolved, '');
            expect(c.value.decimal, 9999);
            expect(identityHashCode(c.resolver.results), results);

        });

        test("isEquation && changed", () {

            var c = new TestCell("-1000.00", 0);
            var results = identityHashCode(c.resolver.results);

            expect(c.canonical, "-1000.00");
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 0);

            c.local = "2+2,000+!";
            c.calculate(columnGetterReturns([18]), changed: true);

            expect(c.canonical, "(2 + 2000) + !");
            expect(c.local, "2+2,000+!");
            expect(c.resolved, "(2 + 2,000) + 18");
            expect(c.value.decimal, 2020);
            expect(identityHashCode(c.resolver.results), results);

        });

    });
}