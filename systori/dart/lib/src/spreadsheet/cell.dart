import 'package:systori/decimal.dart';
import 'range.dart';
import 'equation.dart';


abstract class Cell {

    Decimal value;
    String get equation;
    set resolved(String resolved);
    String get resolved;

    int row;
    int column;
    RangeList ranges;
    RangeCache cache = new RangeCache();

    int _previous_row_position;
    String _previous_equation;

    bool get hasEquation => !Decimal.isNullBlankOrNumber(equation);

    update(List<Cell> getColumn(int columnIdx), bool dependencyChanged) {

        var equationChanged = _previous_equation != equation;
        var positionChanged = _previous_row_position != row;

        if (!hasEquation) {
            if (equationChanged)
                value = new Decimal.parse(equation);
            return;
        }

        if (dependencyChanged || positionChanged)
            // something changed above us or we moved rows
            // invalidate the cache
            cache.reset();

        if (equationChanged || ranges == null)
            // equation changed or was never primed, parse the ranges
            ranges = new RangeList(equation, cache);

        // there are three cases where this will do something:
        // 1) cache was empty to begin with
        // 2) cache was invalidated above
        // 3) user added a new range to equation
        ranges.calculate(getColumn, cache, column);

        // replace all ranges with actual values
        resolved = ranges.resolve(equation);

        // math
        value = solve(resolved);

        _previous_equation = equation;
        _previous_row_position = row;
    }

    onCalculationFinished() {}

}


