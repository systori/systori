import 'common.dart';

int sum(Iterable<int> ints) => ints.reduce((i, j) => i + j);


abstract class SummingSheet {
    List<SummingRow> get rows;
    int calculate() {
        int total = 0;
        List<Equation> previous = [];
        for (var row in rows) {
            var eq = row.calculate(previous);
            previous.add(eq);
            total += eq.total;
        }
        return total;
    }
}


class Range {

    static final RegExp RANGE = new RegExp(r'([!@])(&|\d*)(\[?)(:?)(\]?)(&|\d*)');

    final String direction;
    final bool range;

    final int start;
    final bool isStartEquation;
    final bool isStartExclusive;
    bool get isStartOpen => start == null && !isStartEquation;

    final int end;
    final bool isEndExclusive;
    final bool isEndEquation;
    bool get isEndOpen => end == null && !isEndEquation;

    Range(this.direction, start, exclusiveStart, range, exclusiveEnd, end):
        start = int.parse(start, onError: (source) => 1),
        isStartEquation = start=='&',
        isStartExclusive = exclusiveStart=='[',
        end = int.parse(end, onError: (source) => null),
        isEndExclusive = exclusiveEnd==']',
        isEndEquation = end=='&',
        range = exclusiveStart=='[' || exclusiveEnd==']' || range==':'
    ;

    static List<Range> extractRanges(String eq) =>
        RANGE.allMatches(eq).map((m) =>
            new Range(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))
        ).toList();

    int total;
    int startIdx;
    int endIdx;

    int sum(List<Equation> previous) {
        total = 0;
        startIdx = null;
        endIdx = null;

        Iterator<Equation> rows = previous.iterator;
        if (direction == '!') {
            rows = previous.reversed.iterator;
        }

        int i = 0;
        bool inside = false;
        int lastIdx = previous.length;
        while (rows.moveNext()) { i++;

            if ((!isStartEquation && start == i) || (isStartEquation && rows.current.isEquation)) {
                inside = true;
                if (isStartExclusive)
                    // if we're at the start and [ then don't add this row
                    continue;
            }

            if (!inside)
                continue; // keep searching for the start of range

            if (startIdx == null && endIdx == null) {
                if (direction == '!')
                    endIdx = lastIdx-i;
                else
                    startIdx = i-1;
            }

            if ((!isEndEquation && end == i) || (isEndEquation && rows.current.isEquation) || lastIdx == i)
                // last row means we're not inside anymore
                inside = false;

            if (isEndExclusive && !inside)
                // if we're at the end and ] then don't add this row
                break;

            total += rows.current.total;

            if (direction == '!')
                startIdx = lastIdx-i;
            else
                endIdx = i-1;

            if (!inside || !range)
                break;

        }

        return total;
    }

    bool isHit(int idx) => startIdx <= idx && idx <= endIdx;

}


class Equation {

    final String eq;
    final List<Range> ranges;
    bool get isEquation => ranges.length > 0;
    Equation(eq): ranges = Range.extractRanges(eq), eq=eq;

    int total = 0;
    int price = 0;
    List<int> rowColors; // -1: overlap, 0: no color, 1..: color group
    int calculate(int qty, int _price, List<Equation> previous) {

        total = 0;
        price = _price;
        rowColors = new List.filled(previous.length, 0);

        if (isEquation) {
            price = 0;
            for (var range in ranges) {
                price += range.sum(previous);
            }
            ranges.asMap().forEach((group, range) {
                for (int idx = 0; idx < rowColors.length; idx++) {
                    if (range.isHit(idx)) {
                        if (rowColors[idx] != 0) {
                            rowColors[idx] = -1;
                        } else {
                            rowColors[idx] = group+1;
                        }
                    }
                }
            });

        }

        if (price != null) {
            if (qty == null) qty = 100;
            if (eq.contains('%')) qty = (qty/100).round();
            total = ((qty * price)/100).round();
        } else {
            price = 0;
        }

        return total;

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

    Equation calculate(List<Equation> previous) {
        if (equation == null || equation.eq != unit) {
            equation = new Equation(unit);
        }
        var _qty = string_to_int(qty);
        var _price = string_to_int(price);
        equation.calculate(_qty, _price, previous);
        isPriceCalculated = equation.isEquation;
        price = amount_int_to_string(equation.price);
        total = amount_int_to_string(equation.total);
        onCalculationFinished();
        return equation;
    }

    onCalculationFinished() {}
}