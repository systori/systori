import 'package:test/test.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart' as sheet;


class Cell extends sheet.Cell {
    String equation, resolved;
    Cell(_value, [this.equation="", _col=0, _row=0])
        {value=_value; column=_col; row=_row;}
}


Cell cell(String txt, [num value]) => new Cell(new Decimal(value), txt);

Cell eval(String eq, List<int> ints, [eq1=-1, eq2=-1]) {
    var c = new Cell(new Decimal(), eq, 0, ints.length);
    c.update((col) =>
        enumerate(ints).map((total) =>
            new Cell(
                new Decimal(total.value),
                eq1==total.index||eq2==total.index ? '!' : '',
                col, total.index
            )
        ).toList(), true);
    return c;
}

double calc(String eq, List<int> ints, [eq1=-1, eq2=-1]) =>
    eval(eq, ints, eq1, eq2).value.decimal;


main() async {

    group("Cell attributes", () {

        test("isPrimed", () {
            var c = cell('1');
            expect(c.isPrimed, isFalse);
            c = eval('1', []);
            expect(c.isPrimed, isTrue);
        });

        test("isOnlyNumber", () {
            var c = cell('');
            expect(c.isNotEquation(''), isFalse);
            c = eval('1', []);
            expect(c.isPrimed, isTrue);
            expect(calc('!+!+!', [1,2]), 6);
        });

        test("hasEquation", () {
            var c = cell('1');
            expect(c.isPrimed, isFalse);
            c = eval('1', []);
            expect(c.isPrimed, isTrue);
            expect(calc('!+!+!', [1,2]), 6);
        });

    });

    group("Cell.calculate() with ranges", () {

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