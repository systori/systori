import 'package:test/test.dart';
import 'package:mockito/mockito.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart' as sheet;


class Cell extends sheet.Cell {
    int column;
    Decimal value;
    String rawEquation, resolvedEquation;
    Cell(this.value, [this.rawEquation="", this.column=0]);
}


class MockSpreadsheet extends Mock implements sheet.Spreadsheet {}
sheet.Spreadsheet mockSheet(List<int> ints, int eq1, int eq2) {
    var sheet = new MockSpreadsheet();
    for (var col in range(3)) {
        when(sheet.getColumn(col)).thenReturn(
            enumerate(ints).
            map((total) =>
                new Cell(
                    new Decimal(total.value),
                    eq1==total.index||eq2==total.index ? '!' : '',
                    col
                )
            ).toList()
        );
    }
    return sheet;
}

Cell cell(String txt, [num value]) => new Cell(new Decimal(value), txt);

Cell eval(String eq, List<int> ints, [eq1=-1, eq2=-1]) =>
    cell(eq)..equationChanged(mockSheet(ints, eq1, eq2));

double calc(String eq, List<int> ints, [eq1=-1, eq2=-1]) =>
    eval(eq, ints, eq1, eq2).value.decimal;

List matrix(String eq, List<int> ints, [eq1=-1, eq2=-1]) {
    var c = cell(eq);
    var s = mockSheet(ints, eq1, eq2);
    c.equationChanged(s);
    c.updateRangeMatrix(ints.length);
    return c.rangeMatrix;
}

List flat(String eq, List<int> ints, [eq1=-1, eq2=-1]) =>
    matrix(eq, ints, eq1, eq2).map((row)=>row[0]).toList();


main() async {

    group("Cell attributes", () {

        test("isPrimed", () {
            var c = cell('1');
            expect(c.isPrimed, isFalse);
            c = eval('1', []);
            expect(c.isPrimed, isTrue);
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

    group("Cell.rangeMatrix", () {

        test("single number non-ranges", () {
            expect(flat('!', [1,2,3]), [0,0,1]);
            expect(flat('!@', [1,2,3]), [2,0,1]);
            expect(flat('!!@', [1,2,3]), [2,0,1]);
        });

        test("multiple ranges", () {
            expect(flat('!:', [1,2,3]), [1,1,1]);
            expect(flat('!:@', [1,2,3]), [-1,1,1]);
            expect(flat('!!2@:', [1,2,3]), [3,-1,-1]);
            expect(flat('!!2@', [1,2,3]), [3,2,1]);
        });

        test("multiple column ranges", () {
            expect(
                matrix('A!1C@1', [1,2,3]),
                [[0,0,2],
                 [0,0,0],
                 [1,0,0]]
            );
            expect(
                matrix('A!1-B!2-C!3-C@3-A@1', [1,2,3]),
                [[5,0,3],
                 [0,2,0],
                 [1,0,4]]
            );
        });

    });

}