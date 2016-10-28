@TestOn('vm')
import 'package:test/test.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';


class TestCell extends Cell {
    String canonical, local, resolved;
    TestCell(_value, [canonical="", _col=0, _row=0])
    {value=_value; this.canonical=canonical; this.column=_col; row=_row;}
}


Cell cell(String txt, [num value=0]) => new TestCell(new Decimal(value), txt);

ColumnGetter columnGetterFor(List<int> ints, [eq1=-1, eq2=-1]) =>
    (col) => enumerate(ints).map((total) =>
        new TestCell(
            new Decimal(total.value),
            eq1==total.index||eq2==total.index ? '!' : '',
            col, total.index)).toList();

Cell eval(String eq, List<int> ints, [eq1=-1, eq2=-1]) {
    var c = new TestCell(new Decimal(), eq, 0, ints.length);
    c.update(columnGetterFor(ints, eq1, eq2), true);
    return c;
}

double calc(String eq, List<int> ints, [eq1=-1, eq2=-1]) =>
    eval(eq, ints, eq1, eq2).value.decimal;


main() async {

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
            c.calculate(columnGetterFor([1,2]), false);
            expect(rr.ranges[0].result.group, 1);
            expect(rr.ranges[0].result.start, 1);
            expect(rr.ranges[1].result.start, 1);
        });

    });

    group("Cell.update(): ", () {

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
            expect(calc('!+!+!', [1,2]), 6);
            expect(calc('!2+!2+!2', [1,2]), 3);
            expect(calc('@+@+@', [1,2]), 3);
            expect(calc('@2+@2+@2', [1,2]), 6);
        });

        test("ranges, bottom-up", () {
            expect(calc('!2:4+!5:', [1,2,3,4,5,6]), 15);
            expect(calc('!:3+!5:', [1,2,3,4,5,6]), 18);
            expect(calc('!:2+!4', [1,2,3,4,5,6]), 14);
        });

        test("ranges, top-down", () {
            expect(calc('@2:4+@5:', [1,2,3,4,5,6]), 20);
            expect(calc('@:3+@5:', [1,2,3,4,5,6]), 17);
            expect(calc('@:2+@4', [1,2,3,4,5,6]), 7);
        });

        test("ranges, mixed", () {
            expect(calc('@:2+!:2', [1,2,3,4,5,6]), 14);
            expect(calc('@:3+!:3', [1,2,3,4,5,6]), 21);
            expect(calc('@:+!:', [1,2,3,4,5,6]), 42);
        });

    });

}