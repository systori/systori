@TestOn("vm")
import 'package:test/test.dart';
import 'package:mockito/mockito.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';


class TestCell extends Cell {
    String canonical, local, resolved;
    TestCell(_value, [canonical="", _col=0, _row=0])
    {value=_value; this.canonical=canonical; this.column=_col; this.row=_row;}
}


class TestRow extends Row {
    Cell qty, price, total;
    bool hasPercent=false;
    TestRow(qty, price, total):
        qty = new TestCell(new Decimal(null), qty, 0),
        price = new TestCell(new Decimal(null), price, 1),
        total = new TestCell(new Decimal(null), total, 2);
}


class MockSpreadsheet extends Mock implements Spreadsheet {}
Spreadsheet mockSheet(List<int> ints, int eq1, int eq2) {
    ints = ints != null ? ints : [];
    var sheet = new MockSpreadsheet();
    for (var col in range(3)) {
        when(sheet.getColumn(col)).thenReturn(
            enumerate(ints).
            map((total) =>
            new TestCell(
                new Decimal(total.value),
                eq1==total.index||eq2==total.index ? '!' : '',
                col
            )
            ).toList()
        );
    }
    return sheet;
}


Row row(String qty, String price, String total, [List<int> ints, eq1=-1, eq2=-1]) {
    var r = new TestRow(qty, price, total);
    r.calculate(mockSheet(ints, eq1, eq2), ints!=null?ints.length:0, true);
    return r;
}

double total(String qty, String price, String total, [List<int> ints, eq1=-1, eq2=-1]) =>
    row(qty, price, total, ints, eq1, eq1).total.value.decimal;

double qty(String qty, String price, String total, [List<int> ints, eq1=-1, eq2=-1]) =>
    row(qty, price, total, ints, eq1, eq1).qty.value.decimal;

main() async {

    group("Row.calculate() without ranges", () {

        double percent(String qty, String price) {
            var r = new TestRow(qty, price, '');
            r.hasPercent = true;
            r.calculate(mockSheet([], null, null), 0, true);
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