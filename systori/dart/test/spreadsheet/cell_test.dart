@TestOn('vm')
import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';


class TestCell extends Cell {
    String canonical, local, resolved;
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
    cell(eq, 0, 0, ints.length)..update(columnGetterReturns(ints, eq1, eq2), true);

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
            expect(cell(null).isBlank, isTrue);
            expect(cell('').isBlank, isTrue);
            expect(cell('0').isBlank, isTrue);
            expect(cell('-0.0').isBlank, isTrue);
            expect(cell('-0.1').isBlank, isFalse);
        });

        test("isNumber", () {
            expect(cell(null).isNumber, isFalse);
            expect(cell('').isNumber, isFalse);
            expect(cell('0').isNumber, isTrue);
            expect(cell('-0.0').isNumber, isTrue);
            expect(cell('-0.1').isNumber, isTrue);
        });

        test("isEquation", () {
            expect(cell(null).isEquation, isFalse);
            expect(cell('').isEquation, isFalse);
            expect(cell('0').isEquation, isFalse);
            expect(cell('1,0.0').isEquation, isFalse);
            expect(cell('-10').isEquation, isFalse);
            expect(cell('A').isEquation, isTrue);
            expect(cell('!:').isEquation, isTrue);
            expect(cell('!+!+!').isEquation, isTrue);
        });

        test("isEquationChanged", () {
            var c = cell('');
            expect(c.isEquationChanged, isFalse);

            c.local = '@';
            expect(c.isEquationChanged, isTrue);

            c.update((i)=>[],false);
            expect(c.isEquationChanged, isFalse);

            c.local = '@';
            expect(c.isEquationChanged, isFalse);
            c.local = '!';
            expect(c.isEquationChanged, isTrue);

        });

        test("isEquationChanged", () {
            var c = cell('');

            // always marked as changed on initial load
            expect(c.isPositionChanged, isTrue);

            c.update((i)=>[],false);
            // change saved
            expect(c.isPositionChanged, isFalse);

            c.row = 9;
            // changed
            expect(c.isPositionChanged, isTrue);

        });

        test("RangeResolver.reset()", () {
            Cell c = eval('!+!+!', [1,2]);
            RangeResolver rr = c.resolver;
            expect(rr.results, contains('!'));
            expect(rr.ranges[0].result.start, 1);
            expect(rr.ranges[1].result.start, 1);

            rr.reset();
            expect(rr.results, isEmpty);
            expect(rr.ranges[0].result.group, 1);
            expect(rr.ranges[0].result.start, -1);
            expect(rr.ranges[1].result.start, -1);

            c.resolver.collectRanges = true;
            c.calculate(columnGetterReturns([1,2]), false);
            expect(rr.ranges[0].result.group, 1);
            expect(rr.ranges[0].result.start, 1);
            expect(rr.ranges[1].result.start, 1);
        });

    });

    group("Cell.calculate()", () {

        test("non-equation, blank", () {
            var c = cell('');
            expect(c.value, new Decimal());

            c.update((i)=>[],false);
            expect(c.value, new Decimal());

            c.local = '   ';
            c.update((i)=>[],false);
            expect(c.value, new Decimal());
        });

        test("non-equation, number", () {
            var c = cell('7', 9);
            expect(c.value, new Decimal(9));

            c.update((i)=>[],false);
            expect(c.value, new Decimal(7));

            c.local = '-9,000.00';
            c.changed();
            c.update((i)=>[],false);
            expect(c.value, new Decimal(-9000));
        });

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

    group("Cell phases", () {

        test("cell calculated before being focused", () {
            var c = new TestCell("-1000.00+!:", 98.0);

            // initial
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 98);

            // should only update the cell value
            c.calculate(columnGetterReturns([99]), true);

            // after calculation (not focused)
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, -901);

        });

        test("cell focused", () {
            var c = new TestCell("-1000.00+!:", 98.0);

            // initial
            expect(c.local, isNull);
            expect(c.resolved, isNull);
            expect(c.value.decimal, 98);

            // converts canonical to local so it can be edited
            c.focused();

            // user can now edit the equation
            expect(c.local, "-1,000 + !:");
            expect(c.resolved, isNull);
            expect(c.value.decimal, 98);

            // focusing also triggers a recalculate
            c.calculate(columnGetterReturns([99]), true);

            // finally the resolved and value are updated
            expect(c.local, "-1,000 + !:");
            expect(c.resolved, "-1,000  + 99");
            expect(c.value.decimal, -901);

        });

    });
}