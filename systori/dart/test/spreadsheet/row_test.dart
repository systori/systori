import 'package:test/test.dart';
import 'package:mockito/mockito.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart' as sheet;


class Cell extends sheet.Cell {
    int column;
    Decimal value;
    String rawEquation, resolvedEquation;
    Cell(this.value, this.rawEquation, this.column);
}


class Row extends sheet.Row {
    Cell qty, price, total;
    bool hasPercent=false;
    Row(qty, price, total):
        qty = new Cell(new Decimal(null), qty, 0),
        price = new Cell(new Decimal(null), price, 1),
        total = new Cell(new Decimal(null), total, 2);
}


class MockSpreadsheet extends Mock implements sheet.Spreadsheet {}
sheet.Spreadsheet mockSheet(List<int> ints, int eq1, int eq2) {
    ints = ints != null ? ints : [];
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


Row row(String qty, String price, String total, [List<int> ints, eq1=-1, eq2=-1]) =>
    new Row(qty, price, total)..calculate(mockSheet(ints, eq1, eq2));

double total(String qty, String price, String total, [List<int> ints, eq1=-1, eq2=-1]) =>
    row(qty, price, total, ints, eq1, eq1).total.value.decimal;

double qty(String qty, String price, String total, [List<int> ints, eq1=-1, eq2=-1]) =>
    row(qty, price, total, ints, eq1, eq1).qty.value.decimal;

main() async {

    group("Row.calculate() without ranges", () {

        double percent(String qty, String price) {
            var r = new Row(qty, price, '');
            r.hasPercent = true;
            r.calculate(mockSheet([], null, null));
            return r.total.value.decimal;
        }

        test("basic calculation for qty", () {
            expect(qty('', '7', '21'), 3.00);
            expect(qty('', '5', '2.5'), 0.50);
        });

        test("basic calculation for total", () {
            expect(total('2', '3', ''), 6.00);
            expect(total('2', '5', ''), 10.00);
        });

        test("percent", () {
            expect(percent('20', '12'), 2.40);
        });

        test("##/unit", () {
            var r = row('7', '', '21');
            expect(r.price.value.money, '3.00');
            expect(r.total.value.money, '21.00');
        });

    });

}