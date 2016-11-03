import 'package:systori/decimal.dart';
import 'cell.dart';


abstract class Row {

    Cell get qty;
    Cell get price;
    Cell get total;
    bool get hasPercent;

    List<Cell> get columns => [qty, price, total];
    Cell getCell(int cell) => columns[cell];

    calculate(ColumnGetter getColumn, int row, bool dependenciesChanged) {

        qty.column = 0;
        price.column = 1;
        total.column = 2;

        columns.forEach((cell) {
            cell.row = row;
            cell.calculate(getColumn, dependenciesChanged);
        });

        solve();

    }

    solve() {

        var _qty = qty.value;
        if (hasPercent && qty.isCanonicalNotBlank)
            _qty = qty.value / new Decimal(100);

        if (qty.isCanonicalNotBlank && price.isCanonicalNotBlank && total.isCanonicalBlank)
            total.setCalculated(_qty * price.value); else
        if (qty.isCanonicalNotBlank && price.isCanonicalBlank    && total.isCanonicalNotBlank)
            price.setCalculated(total.value / _qty); else
        if (qty.isCanonicalBlank    && price.isCanonicalNotBlank && total.isCanonicalNotBlank)
            qty.setCalculated(total.value / price.value);

    }

}
