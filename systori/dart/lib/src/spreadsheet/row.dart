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

    calculate(Spreadsheet sheet, int row, Cell changedCell,
        {focused: false, changed: false, moved: false}) {

        enumerate/*<Cell>*/(columns).forEach((IndexedValue<Cell> iterator) {
            var cell = iterator.value;
            cell.row = row;
            cell.column = iterator.index;
            cell.calculate(sheet.getColumn,
                focused: cell==changedCell && focused,
                changed: cell==changedCell && changed,
                dependenciesChanged: (changedCell.row != -1 && changed) || moved
            );
        });

        var rowChanged = (changedCell.row == row || changedCell.row != -1) && changed;

        if (rowChanged || moved) {
            solve();
        }

        columns.forEach((cell) => cell.onRowCalculationFinished());
        onRowCalculationFinished();

    }

    solve() {

        var _qty = qty.value;
        if (hasPercent && qty.isCanonicalNotBlank)
            _qty = qty.value / new Decimal(100);

        if (qty.isCanonicalNotBlank && price.isCanonicalNotBlank && total.isCanonicalBlank)
            total.value = _qty * price.value; else
        if (qty.isCanonicalNotBlank && price.isCanonicalBlank    && total.isCanonicalNotBlank)
            price.value = total.value / _qty; else
        if (qty.isCanonicalBlank    && price.isCanonicalNotBlank && total.isCanonicalNotBlank)
            qty.value = total.value / price.value;

    }

    onRowCalculationFinished();
}
