import 'package:systori/decimal.dart';
import 'range.dart';
import 'equation.dart';


abstract class Cell extends Equation {

    int row;
    int column;

    int _previous_row_position;
    String _previous_equation;

    static final RegExp ZERO = new RegExp(r"^-?[0.,]*$");
    static final RegExp NUMBER = new RegExp(r"^-?[0-9.,]+$");
    bool _isBlankOrZero(String txt) => txt.isEmpty || ZERO.hasMatch(txt);
    /*
        Cell has three states:
          1) Blank: null, empty or 0
          2) Number: valid number (including 0)
          3) Equation: not Blank and not Number
     */
    bool get isBlank => canonical == null || _isBlankOrZero(canonical.trim());
    bool get isNumber =>  canonical != null && NUMBER.hasMatch(canonical.trim());
    bool get isEquation => !isBlank && !isNumber;
    bool get isNotBlank => !isBlank;

    bool get isEquationChanged => _previous_equation != canonical;
    bool get isPositionChanged => _previous_row_position != row;

    update(List<Cell> getColumn(int columnIdx), bool dependencyChanged) {

        if (!isEquation) {

            value = isBlank ? new Decimal() : new Decimal.parse(canonical);

        } else {

            value = new Decimal();

            if (dependencyChanged || isPositionChanged)
                // something changed above us or we moved rows
                // invalidate the cache
                cache.reset();

            if (isEquationChanged || ranges == null)
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
        }

        _previous_equation = equation;
        _previous_row_position = row;
    }

    onCalculationFinished() {}

}
