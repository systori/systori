import 'package:test/test.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart' as sheet;
import 'package:systori/spreadsheet.dart' show Range, RangeList, RangeCache;


class Cell extends sheet.Cell {
    String equation, resolved;
    Cell(_value, [this.equation="", _col=0, _row=0])
        {value=_value; this.column=_col; row=_row;}
}


RangeList ranges(String eq) => new RangeList(eq, new RangeCache());

Range extract(String eq) => ranges(eq).first;

List<Cell> column(List<int> ints, eq1, eq2) =>
    enumerate(ints).map((total) =>
        new Cell(new Decimal(total.value),
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

    group("RangeList()", () {

        test("ranges", () {
            expect(ranges('1+1').length, 0);
            expect(ranges('(1+1)-A@7').length, 1);
            expect(ranges('(1+!&(1/!))-A@7').length, 3);
        });

        test("column", () {
            expect(extract('@').column, null);
            expect(extract('a@').column, 0);
            expect(extract('C@').column, 2);
            expect(extract('D@').column, null);
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