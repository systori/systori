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

    update(Spreadsheet sheet, int row, bool dependencyChanged) {
        enumerate/*<Cell>*/(columns).forEach((IndexedValue<Cell> iterator) {
            iterator.value.row = row;
            iterator.value.column = iterator.index;
            iterator.value.update(sheet.getColumn, dependencyChanged);
        });
    }

    solve() {

        var _qty = qty.value;
        if (hasPercent && qty.isNotBlank)
            _qty = qty.value / new Decimal(100);

        if (qty.isNotBlank && price.isNotBlank && total.isBlank)
            total.value = _qty * price.value; else
        if (qty.isNotBlank && price.isBlank    && total.isNotBlank)
            price.value = total.value / _qty; else
        if (qty.isBlank    && price.isNotBlank && total.isNotBlank)
            qty.value = total.value / price.value; else
        if (qty.isBlank    && price.isBlank    && total.isNotBlank) {
            qty.value = new Decimal(1);
            price.value = total.value;
        }

    }

    onCalculationFinished() {
        columns.forEach((cell) => cell.onCalculationFinished());
    }

    calculate(Spreadsheet sheet, int row, bool dependencyChanged) {
        update(sheet, row, dependencyChanged);
        solve();
        onCalculationFinished();
    }
}
