import 'package:systori/decimal.dart';
import 'cell.dart';

class Range {

    static final RegExp RANGE = new RegExp(r'([ABC]?)([!@])(&?)(\d*)(\[?)(:?)(\]?)(&?)(\d*)');

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

    final int group;
    final int srcStart;
    final int srcEnd;
    final String src;

    Range(this.group, String column, this.direction,
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

    static List<Range> extractRanges(String eq) {
        int i = 1;
        List<Range> ranges = [];
        Map<String,int> rangeGroups = {};
        for (var m in RANGE.allMatches(eq.toUpperCase())) {
            var key = m.group(0);
            if (!rangeGroups.containsKey(key)) {
                rangeGroups[key] = i++;
            }
            ranges.add(new Range(rangeGroups[key], m.group(1), m.group(2),
                m.group(3), m.group(4), // startEquation, start
                m.group(5), m.group(6), m.group(7), // exclusive range
                m.group(8), m.group(9), // endEquation, end
                m.start, m.end, key
            ));
        }
        return ranges;
    }

    static String resolveRanges(String equation, List<Range> ranges, Map<String,Decimal> cache) {
        var buffer = new StringBuffer();
        int lastEnd = 0;
        for (var range in ranges) {
            buffer.write(equation.substring(lastEnd, range.srcStart));
            buffer.write(cache[range.src].number);
            lastEnd = range.srcEnd;
        }
        buffer.write(equation.substring(lastEnd));
        return buffer.toString();
    }

    int startIdx = -1;
    int endIdx = -1;

    Decimal calculate(List<Cell> column) {
        // Due to caching only the first encountered unique range gets calculate()'ed
        // This means that only one of them will have the startIdx/endIdx set.
        startIdx = -1;
        endIdx = -1;

        var total = new Decimal();

        if ((end != null && !isEndEquation && start > end) ||
            (isStartEquation && start > 1 && isEndEquation && isEndOpen)) // prevent: !&2:&
            return total; // stupid users! :-D

        Iterator<Cell> cells = column.iterator;
        if (direction == '!') {
            cells = column.reversed.iterator;
        }

        int i = 0;
        bool inside = false;
        int equationIdx = 0;
        int lastIdx = column.length;
        while (cells.moveNext()) { i++;

        if (cells.current.hasEquation) equationIdx++;

        if ((!isStartEquation && start == i) ||
            (isStartEquation && cells.current.hasEquation && start == equationIdx)) {
            inside = true;
            if (isStartExclusive)
                // if we're at the start and [ then don't add this row
                continue;
        }

        if (!inside)
            continue; // keep searching for the start of range

        if (startIdx == -1 && endIdx == -1) {
            if (direction == '!')
                endIdx = lastIdx-i;
            else
                startIdx = i-1;
        }

        if ((!isEndEquation && end == i) ||
            (isEndEquation && cells.current.hasEquation && end == equationIdx) ||
            lastIdx == i) {
            // last row means we're not inside anymore
            inside = false;
            if (isEndExclusive)
                // if we're at the end and ] then don't add this row, break immediately
                break;
            if (lastIdx == i && isEndEquation && (!cells.current.hasEquation || end != equationIdx)) {
                // we've made it to the end without finding any equations
                // this whole range is a dud, clear everything and exit
                total = new Decimal();
                startIdx = -1;
                endIdx = -1;
                break;
            }
        }

        total += cells.current.value;

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

