@TestOn("vm")
import 'package:test/test.dart';
import 'package:systori/numbers.dart';
import 'package:systori/spreadsheet.dart';
import 'cell_test.dart';


class TestRow extends Row {
    Cell qty;
    Cell price;
    Cell total;
    bool hasPercent=false;
    bool is_hidden=false;
    TestRow(String qty, String price, String total, [hasPercent = false]):
        qty = new TestCell(qty, qty, 0),
        price = new TestCell(price, price, 1),
        total = new TestCell(total, total, 2),
        hasPercent = hasPercent;
    TestRow.dartSdkBug27754(qty, price, total, hasPercent):
            this(qty, price, total, hasPercent);
}


class TestTotalRow extends TestRow with TotalRow {
    Decimal diff;
    TestTotalRow(String qty, String price, String total, [hasPercent = false]):
            super.dartSdkBug27754(qty, price, total, hasPercent);
    setDiff(Decimal decimal) => diff = decimal;
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

        test("reset previously calculated cells when calculation not possible", () {
            var r = new TestRow('2', '2', '');

            r.calculate((i)=>[], 0, false);
            expect(r.total.text, '4.00');
            expect(r.total.value.decimal, 4);

            r.qty.focused();
            r.calculate((i)=>[], 0, false);
            r.qty.text = '';

            r.calculate((i)=>[], 0, false);
            expect(r.total.text, '');
            expect(r.total.value.decimal, 0);
        });

    });

    group("TotalRow.calculate()", () {

        test("can't calculate", () {
            var r = new TestTotalRow('', '', '');
            r.calculateTotal(new Decimal(5, 3));
            expect(r.qty.value.decimal, null);
            expect(r.price.value.decimal, 5);
            expect(r.total.value.decimal, null);
            expect(r.diff.decimal, 0);
        });

        test("fully calculated", () {
            var r = new TestTotalRow('3', '', '');
            r.calculateTotal(new Decimal(5, 3));
            expect(r.qty.value.decimal, 3);
            expect(r.price.value.decimal, 5);
            expect(r.total.value.decimal, 15);
            expect(r.diff.decimal, 0);
        });

        test("reverse calculating price", () {
            var r = new TestTotalRow('3', '2', '');
            r.calculateTotal(new Decimal(5, 3));
            expect(r.qty.value.decimal, 3);
            expect(r.price.value.decimal, 2);
            expect(r.total.value.decimal, 6);
            expect(r.diff.decimal, -3);
        });

        test("reverse calculating total", () {
            var r = new TestTotalRow('3', '', '12');
            r.calculateTotal(new Decimal(2, 3));
            expect(r.qty.value.decimal, 3);
            expect(r.price.value.decimal, 4);
            expect(r.total.value.decimal, 12);
            expect(r.diff.decimal, 2);
        });

    });
}