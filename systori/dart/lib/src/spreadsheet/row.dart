import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'spreadsheet.dart';
import 'cell.dart';


abstract class Row {

    Cell get qty;
    Cell get price;
    Cell get total;
    bool get hasPercent;

    List<Cell> get columns => [qty, price, total];
    Cell getCell(int cell) => columns[cell];

    calculate(Spreadsheet sheet, int row, bool dependencyChanged) {

        enumerate(columns).forEach((IndexedValue<Cell> iterator) {
            iterator.value.row = row;
            iterator.value.column = iterator.index;
            iterator.value.update(sheet.getColumn, dependencyChanged);
        });

        var _qty = qty.value;
        if (hasPercent && _qty.isNotNull)
            _qty = qty.value / new Decimal(100);

        if (_qty.isNotNull && price.value.isNotNull) {
            total.value = _qty * price.value;
        } else if (_qty.isNotNull && total.value.isNotNull) {
            price.value = total.value / _qty;
        } else if (price.value.isNotNull && total.value.isNotNull) {
            qty.value = total.value / price.value;
        }

        // give the UI a chance to do something in response
        columns.forEach((cell) => cell.onCalculationFinished());

    }

}
