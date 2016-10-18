import 'common.dart';

int sum(Iterable<int> ints) => ints.reduce((i, j) => i + j);


abstract class SummingSheet {
    List<SummingRow> get rows;
    int calculate() {
        List<int> subtotals = [];
        for (var row in rows) {
            subtotals.add(row.calculate(subtotals));
        }
        return subtotals.length >0 ? sum(subtotals) : 0;
    }
}


class Equation {

    static final RegExp SUMX = new RegExp(r'[%!](\d+)');

    int sumX = 1;
    bool isSum;
    bool isSumAll;
    bool isPercent;

    Equation(String eq) {
        isPercent = eq.contains('%');
        isSum = eq.contains('!') || isPercent;
        isSumAll = eq.contains('!!');
        if (!isSumAll) {
            var match = SUMX.firstMatch(eq);
            if (match != null) {
                sumX = int.parse(match.group(1));
            }
        }
    }

    int calculate(List<int> previous) {
        if (!isSum) return null;

        if (previous.length == 0) {
            sumX = 0;
            return 0;
        }

        if (isSumAll || previous.length < sumX) {
            sumX = previous.length;
            return sum(previous);
        } else {
            var toSumRow = previous.length - sumX;
            return sum(previous.skip(toSumRow));
        }
    }
}


abstract class SummingRow {

    Equation equation;

    String get qty;
    String get unit;
    String get price;
    set price(String _price);
    set isPriceCalculated(bool _calculated);
    String get total;
    set total(String _total);

    int calculate(List<int> previous) {
        equation = new Equation(unit);
        var _qty = string_to_int(qty);
        var _calc = equation.calculate(previous);
        var _price;
        if (_calc != null) {
            _price = _calc;
            price = amount_int_to_string(_calc);
            isPriceCalculated = true;
        } else {
            _price = string_to_int(price);
            isPriceCalculated = false;
        }

        var _total = 0;

        if (_price != null) {
            if (_qty == null) _qty = 100;
            if (equation.isPercent) _qty /= 100;
            _total = ((_qty * _price)/100).round();
        }

        total = amount_int_to_string(_total);
        onCalculationFinished();
        return _total;
    }

    onCalculationFinished() {}
}