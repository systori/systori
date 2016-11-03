import 'package:systori/decimal.dart';
import 'row.dart';
import 'cell.dart';


abstract class Spreadsheet {

    List<Row> get rows;
    List<Row> iterated;
    bool get hasNeverBeenCalculated => iterated == null;

    Decimal calculate(Cell changedCell, {focused: true}) {
        iterated = [];
        Decimal total = new Decimal();
        changedCell.row = -1;
        int rowNum = 0;
        for (var row in rows) {
            row.calculate(this.getColumn, rowNum++, !focused && changedCell.row != -1);
            total += row.total.value;
            iterated.add(row);
        }
        onCalculationFinished(changedCell);
        return total;
    }

    onCalculationFinished(Cell changedCell);

    List<Cell> getColumn(int column) =>
        iterated.map((Row row) => row.getCell(column)).toList();

}

