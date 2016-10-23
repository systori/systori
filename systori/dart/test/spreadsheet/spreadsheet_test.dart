import 'package:test/test.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart' as sheet;


class Cell extends sheet.Cell {
    String equation, resolved;
    Cell(_value, [this.equation="", _col=0, _row=0])
        {value=_value; column=_col; row=_row;}
}


class Row extends sheet.Row {
    Cell qty, price, total;
    bool hasPercent=false;
    Row(qty, unit, price, total):
            qty = new Cell(new Decimal(null), qty, 0),
            hasPercent = unit.contains('%'),
            price = new Cell(new Decimal(null), price, 1),
            total = new Cell(new Decimal(null), total, 2);
}

class Spreadsheet extends sheet.Spreadsheet {
    List<Row> rows;
    Spreadsheet(this.rows);
}


main() async {

    group("Spreadsheet", () {

        row(q,u,p,t) => new Row(q,u,p,t);
        firstCell(sheet) => sheet.rows[0].columns[0];

        var sheet;

        test("Spreadsheet.calculate()", () {

            sheet = new Spreadsheet([]);
            expect(sheet.calculate(new Cell(new Decimal())).decimal, 0);

            sheet = new Spreadsheet([row('1', 'm', '1', '')]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 1.00);

            sheet = new Spreadsheet([
                row('1', 'm', '7', ''),
                row('1', 'm', '7', ''),
                row('2', 'm', '3', ''),  // 20
                row('50', '%', 'C!:', ''),  // 50% of 20 = 10
            ]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 30.00);

            sheet = new Spreadsheet([
                row('1', 'm', '7', ''),
                row('1', 'm', '7', ''),
                row('2', 'm', '3', ''),
                row('50', '%', 'C!', ''),  // 50% of 6 = 3
            ]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 23.00);

            sheet = new Spreadsheet([
                row('1', 'm', '7', ''),
                row('1', 'm', '7', ''),
                row('2', 'm', '3', ''),
                row('', '', '2', '!:3'),  // qty:sum(20)/2=10 price:2 = 20
            ]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 40.00);

            sheet = new Spreadsheet([
                row('1', 'm', '7', ''), //               7.00
                row('1', 'm', '7', ''), //               7.00
                row('10', '%', '!:', ''), // 10% of 14 = 1.40
                row('2', 'm', '3', ''), //               6.00
                row('', '', '', '!:2'), //               7.40
            ]);
            expect(sheet.calculate(firstCell(sheet)).decimal, 28.80);

        });

    });
}