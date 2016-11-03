@TestOn("vm")
import 'package:test/test.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';
import 'cell_test.dart';
import 'row_test.dart';


class TestSpreadsheet extends Spreadsheet {
    List<TestRow> rows;
    TestSpreadsheet(this.rows);
    @override
    onCalculationFinished(Cell changedCell) {}
}


main() async {

    group("Spreadsheet", () {

        row(q,p,t,[percent=false]) => new TestRow(q,p,t,percent);
        firstCell(sheet) => sheet.rows[0].columns[0];

        var sheet;

        test("Spreadsheet.calculate()", () {

            sheet = new TestSpreadsheet([]);
            expect(sheet.calculate(new TestCell()).decimal, 0);

            sheet = new TestSpreadsheet([row('1', '1', '')]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 1.00);

            sheet = new TestSpreadsheet([
                row('1', '7', ''),
                row('1', '7', ''),
                row('2', '3', ''),  // 20
                row('50', 'C!:', '', true),  // 50% of 20 = 10
            ]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 30.00);

            sheet = new TestSpreadsheet([
                row('1', '7', ''),
                row('1', '7', ''),
                row('2', '3', ''),
                row('50', 'C!', '', true),  // 50% of 6 = 3
            ]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 23.00);

            sheet = new TestSpreadsheet([
                row('1', '7', ''),
                row('1', '7', ''),
                row('2', '3', ''),
                row('',  '2', '!:3'),  // qty:sum(20)/2=10 price:2 = 20
            ]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 40.00);

            sheet = new TestSpreadsheet([
                row('1', '7', ''), //               7.00
                row('1', '7', ''), //               7.00
                row('10', '!:', '', true), // 10% of 14 = 1.40
                row('2', '3', ''), //               6.00
                row('', '', '!:2'), //               7.40
            ]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 28.80);

        });

    });
}