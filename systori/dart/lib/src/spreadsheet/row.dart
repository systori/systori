import 'package:systori/decimal.dart';
import 'spreadsheet.dart';
import 'cell.dart';


abstract class Row {

    Cell get qty;
    Cell get price;
    Cell get total;
    bool get hasPercent;

    Cell getCell(int cell) {
        switch (cell) {
            case 0: return qty;
            case 1: return price;
            case 2: return total;
        }
        return null;
    }

    calculate(Spreadsheet sheet) {
        qty.dependenciesChanged(sheet);
        price.dependenciesChanged(sheet);
        total.dependenciesChanged(sheet);

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
        onCalculationFinished();
    }

    onCalculationFinished() {}

}
