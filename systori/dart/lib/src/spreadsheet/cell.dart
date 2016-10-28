import 'package:systori/decimal.dart';
import 'equation.dart';


abstract class Cell extends Equation {

    int row;
    int column;

    int _previous_row_position;
    String _previous_local;

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

    bool get isEquationChanged => _previous_local != local;
    bool get isPositionChanged => _previous_row_position != row;

    update(ColumnGetter getColumn, bool dependencyChanged) {

        if (_previous_local == null)
            _previous_local = local;

        if (!isEquation) {

            value = isBlank ? new Decimal() : new Decimal.parse(canonical);

        } else {

            if (isEquationChanged) changed();

            calculate(getColumn, dependencyChanged || isPositionChanged);

        }

        _previous_local = local;
        _previous_row_position = row;
    }

    onCalculationFinished() {}

}
