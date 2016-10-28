import 'package:systori/decimal.dart';
import 'cell.dart';


typedef List<Cell> ColumnGetter(int columnIdx);


class RangeResult {

    int group;
    int start;
    int end;
    Decimal value;

    bool isHit(int idx) => start <= idx && idx <= end;
    bool get isEmpty => start == -1;

    RangeResult() {
        reset();
    }

    reset() {
        start = -1;
        end = -1;
        value = new Decimal();
    }
}


class Range {

    final int column;
    final String direction;
    final bool range;

    final int start;
    final bool isStartEquation;
    final bool isStartExclusive;

    final int end;
    final bool isEndExclusive;
    final bool isEndEquation;
    bool get isEndOpen => end == null && !isEndEquation;

    final RangeResult result;
    final int srcStart;
    final int srcEnd;
    final String src;

    Range(this.result, String column, this.direction,
        startEquation, start,
        exclusiveStart, range, exclusiveEnd,
        endEquation, end,
        this.srcStart, this.srcEnd, this.src):
            column = column.isNotEmpty ? 'ABC'.indexOf(column) : null,
            isStartEquation = startEquation=='&',
            start = int.parse(start, onError: (source) => 1),
            isStartExclusive = exclusiveStart=='[',
            range = exclusiveStart=='[' || exclusiveEnd==']' || range==':',
            isEndExclusive = exclusiveEnd==']',
            isEndEquation = endEquation=='&',
            end = int.parse(end, onError: (source) => endEquation=='&' ? 1 : null)
    ;

    Decimal calculate(List<Cell> _cells) {

        result.reset();

        if ((end != null && !isEndEquation && start > end) ||
            (isStartEquation && start > 1 && isEndEquation && isEndOpen)) // prevent: !&2:&
            return result.value;

        Iterator<Cell> cells = _cells.iterator;
        if (direction == '!') {
            cells = _cells.reversed.iterator;
        }

        int i = 0;
        bool inside = false;
        int equationIdx = 0;
        int lastIdx = _cells.length;
        while (cells.moveNext()) { i++;

        if (cells.current.isEquation) equationIdx++;

        if ((!isStartEquation && start == i) ||
            (isStartEquation && cells.current.isEquation && start == equationIdx)) {
            inside = true;
            if (isStartExclusive)
                // if we're at the start and [ then don't add this row
                continue;
        }

        if (!inside)
            continue; // keep searching for the start of range

        if (result.start == -1 && result.end == -1) {
            if (direction == '!')
                result.end = lastIdx-i;
            else
                result.start = i-1;
        }

        if ((!isEndEquation && end == i) ||
            (isEndEquation && cells.current.isEquation && end == equationIdx) ||
            lastIdx == i) {
            // last row means we're not inside anymore
            inside = false;
            if (isEndExclusive)
                // if we're at the end and ] then don't add this row, break immediately
                break;
            if (lastIdx == i && isEndEquation && (!cells.current.isEquation || end != equationIdx)) {
                // we've made it to the end without finding any equations
                // this whole range is a dud, clear everything and exit
                result.reset();
                break;
            }
        }

        result.value += cells.current.value;

        if (direction == '!')
            result.start = lastIdx-i;
        else
            result.end = i-1;

        if (!inside || !range)
            break;

        }

        return result.value;
    }

}

