import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'row.dart';
import 'cell.dart';


abstract class Spreadsheet {

    List<Row> get rows;
    List<Row> iterated;
    bool get hasNeverBeenCalculated => iterated == null;

    Decimal calculate(Cell changedCell) {
        iterated = [];
        Decimal total = new Decimal();
        changedCell.row = -1;
        changedCell.column = -1;
        enumerate/*<Row>*/(rows).forEach((IndexedValue<Row> iterator) {
            iterator.value.calculate(this, iterator.index, changedCell.row!=-1);
            total += iterator.value.total.value;
            iterated.add(iterator.value);
        });
        onCalculationFinished(changedCell);
        return total;
    }

    onCalculationFinished(Cell changedCell) {}

    List<Cell> getColumn(int column) =>
        iterated.map((Row row) => row.getCell(column)).toList();

}

