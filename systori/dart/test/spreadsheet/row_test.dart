@TestOn("vm")
import 'package:test/test.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';
import 'cell_test.dart';


class TestRow extends Row {
    Cell qty;
    Cell price;
    Cell total;
    bool hasPercent=false;
    TestRow(qty, price, total, [hasPercent = false]):
        qty = new TestCell(qty, qty, 0),
        price = new TestCell(price, price, 1),
        total = new TestCell(total, total, 2),
        hasPercent = hasPercent;
}

Row row(String qty, String price, String total, [hasPercent=false]) =>
    new TestRow(qty, price, total, hasPercent);

Row eval(String qty, String price, String total, List<int> ints, {eq1=-1, eq2=-1, hasPercent=false}) =>
    row(qty, price, total, hasPercent)
        ..calculate(getColumnReturns(ints.map((v)=>v.toString()).toList(), eq1, eq2), ints.length, true);

double total(String qty, String price, String total, {List<int> ints=null, eq1=-1, eq2=-1, hasPercent=false}) =>
    eval(qty, price, total, ints==null?[]:ints, eq1:eq1, eq2:eq2, hasPercent:hasPercent).total.value.decimal;

double price(String qty, String price, String total, [List<int> ints, eq1=-1, eq2=-1]) =>
    eval(qty, price, total, ints==null?[]:ints, eq1:eq1, eq2:eq2).price.value.decimal;

double qty(String qty, String price, String total, [List<int> ints, eq1=-1, eq2=-1]) =>
    eval(qty, price, total, ints==null?[]:ints, eq1:eq1, eq2:eq2).qty.value.decimal;


main() {

    group("Row.calculate()", () {

        test("qty", () {
            expect(qty('', '7', '21'), 3.00);
            expect(qty('', '5', '2.5'), 0.50);
        });

        test("price", () {
            expect(price('7', '', '21'), 3.00);
        });

        test("total", () {
            expect(total('2', '3', ''), 6.00);
            expect(total('2', '5', ''), 10.00);
        });

        test("percent", () {
            expect(total('20', '12', '', hasPercent: true), 2.40);
        });

    });

}