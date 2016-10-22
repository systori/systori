import 'package:systori/decimal.dart';
import 'row.dart';
import 'cell.dart';


abstract class Spreadsheet {

    List<Row> get rows;
    List<Row> iterated;

    Decimal calculate() {
        iterated = [];
        Decimal total = new Decimal();
        for (var row in rows) {
            row.calculate(this);
            total += row.total.value;
            iterated.add(row);
        }
        return total;
    }

    Iterable<Cell> getColumn(int column) =>
        iterated.map((Row row) => row.getCell(column));
}

