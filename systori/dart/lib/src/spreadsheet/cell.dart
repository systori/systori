import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';
import 'package:parsers/parsers.dart' as _p;


typedef List<Cell> ColumnGetter(int columnIdx);


abstract class Cell {

    int row;
    int column;

    String get canonical;
    set canonical(String canonical);

    String get local;
    set local(String local);

    String get resolved;
    set resolved(String resolved);

    Decimal value;

    RangeResolver resolver = new RangeResolver();

    int _previous_row_position;
    String _previous_local;
    bool get isEquationChanged => _previous_local != local;
    bool get isPositionChanged => _previous_row_position != row;

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

    /*
        Cell has phases:
          1) Initial load from server, canonical and result.
          2) Created row, all nulls/blanks.
          2) Focused, local set from canonical.
          4) Calculated, resolved set from local.
     */
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

    focused() { // setup local if this is the first time we focus here
        if (local == null || local.isEmpty)
            local = canonicalToLocal(canonical);
        return local;
    }

    changed() { // underlying local changed (due to user edit of equation)
        canonical = localToCanonical(local);
        resolver.collectRanges = true;
    }

    calculate(ColumnGetter getColumn, dependenciesChanged) {

        resolver.thisColumn = column;
        resolver.getColumn = getColumn;

        if (dependenciesChanged)
            resolver.reset();

        if (resolver.collectRanges && local != null) {
            resolved = localToResolved(local);
            resolver.collectRanges = false;
        }

        value = eval(canonical);
        resolver.collectRanges = false;

    }

    onCalculationFinished() {}

    ParseEquation<String> _canonicalToLocal;
    ParseEquation<String> get canonicalToLocal {
        if (_canonicalToLocal == null)
            _canonicalToLocal = new ConvertEquation(ConvertEquation.canonicalToLocal);
        return _canonicalToLocal;
    }

    ParseEquation<String> _localToCanonical;
    ParseEquation<String> get localToCanonical {
        if (_localToCanonical == null)
            _localToCanonical = new ConvertEquation(ConvertEquation.localToCanonical);
        return _localToCanonical;
    }

    ParseEquation<String> _localToResolved;
    ParseEquation<String> get localToResolved {
        if (_localToResolved == null)
            _localToResolved = new ConvertEquation(ConvertEquation.passThrough, resolver);
        return _localToResolved;
    }

    EvaluateEquation _eval;
    EvaluateEquation get eval {
        if (_eval == null)
            _eval = new EvaluateEquation(resolver);
        return _eval;
    }

}


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


class RangeResolver {

    int thisColumn;
    ColumnGetter getColumn;
    bool _collectRanges = true;
    bool get collectRanges => _collectRanges;
    set collectRanges(bool collect) {
        if (collect) {
            nextGroup = 1;
            ranges = [];
        }
        _collectRanges = collect;
    }

    int nextGroup = 1;
    List<Range> ranges = [];
    Map<String,RangeResult> results = {};

    reset() {
        results.values.forEach((r)=>r.reset());
        results.clear();
    }

    Decimal resolve(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end, startIdx, endIdx, src) {

        if (results.containsKey(src) && !collectRanges) {
            // short circuit
            return results[src].value;
        }

        var result = results.putIfAbsent(src, ()=>new RangeResult());
        if (result.group == null)
            result.group = nextGroup++;

        var range = new Range(
            result, column, direction,
            startEquation, start,
            startExclusive, colon, endExclusive,
            endEquation, end,
            startIdx, endIdx, src
        );

        if (collectRanges)
            ranges.add(range);

        if (result.isEmpty) {
            var columnIdx = range.column != null ? range.column : thisColumn;
            range.calculate(getColumn(columnIdx));
        }

        return result.value;
    }
}



abstract class ParseEquation<R> {

    _p.Parser<R> parser;
    RangeResolver resolver;
    ParseEquation(this.resolver) {
        parser = buildParser();
    }

    R call(String eq);
    R parseDecimal(sign, digits);
    R parseRange(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, _p.PointedValue<String> end);

    String rangeToString(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, _p.PointedValue<String> end) =>
        "${column.value}$direction$startEquation$start$startExclusive$colon$endExclusive$endEquation${end.value}";

    Decimal evalRange(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, _p.PointedValue<String> end) {
        var src = rangeToString(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);
        return resolver.resolve(
            column.value, direction,
            startEquation, start,
            startExclusive, colon, endExclusive,
            endEquation, end.value,
            column.position.offset, end.position.offset, src
        );
    }

    _p.Parser<R> buildParser() => expr() < (_p.eof as _p.Parser<R>);

    _p.Parser<R> lexeme(_p.Parser<R> parser) => parser < (_p.spaces as _p.Parser<R>);
    _p.Parser<R> token(str)               => lexeme(_p.string(str) as _p.Parser<R>);
    _p.Parser<R> parens(parser)           => parser.between(token('('), token(')')) as _p.Parser<R>;

    get times  => token('*');
    get div    => token('/');
    get plus   => token('+');
    get minus  => token('-');

    _p.Parser<R> get sign => (_p.char('-') | _p.char('+')).orElse('') as _p.Parser<R>;
    _p.Parser<R> get digits => _p.oneOf("1234567890.") % 'digit' as _p.Parser<R>;
    _p.Parser<R> get decimal => (lexeme(sign) + digits.many1 ^ parseDecimal) % 'decimal' as _p.Parser<R>;

    _p.Parser<R> get range =>
           (_p.oneOf('ABC').orElse('').withPosition % 'column' +
            _p.oneOf('@!') % 'direction' +
            _p.char('&').orElse('') % 'equation symbol' +
            (_p.digit.many1 ^ (s)=>s.join()).orElse('') % 'row' +
            _p.char('[').orElse('') % 'exclusive range' +
            _p.char(':').orElse('') % 'colon' +
            _p.char(']').orElse('') % 'exclusive range' +
            _p.char('&').orElse('') % 'equation symbol' +
            (_p.digit.many1 ^ (s)=>s.join()).orElse('').withPosition % 'row'
            ^ parseRange) as _p.Parser<R>;

    rec(_p.Parser<R> f()) => _p.rec(f) as _p.Parser<R>;
    _p.Parser<R> expr() => rec(term).chainl1(addop) as _p.Parser<R>;
    _p.Parser<R> term() => rec(atom).chainl1(mulop) as _p.Parser<R>;
    _p.Parser<R> atom() => lexeme(range) | lexeme(decimal) | parens(rec(expr)) as _p.Parser<R>;

    get addop => (plus  > _p.success((x, y) => x + y))
               | (minus > _p.success((x, y) => x - y));

    get mulop => (times > _p.success((x, y) => x * y))
               | (div   > _p.success((x, y) => x / y));
}


class EvaluateEquation extends ParseEquation<Decimal> {

    EvaluateEquation(resolver): super(resolver);

    Decimal call(String eq) => parser.parse(eq.trim());

    Decimal parseDecimal(sign, digits) => new Decimal.parse(sign+digits.join());

    Decimal parseRange(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, _p.PointedValue<String> end) =>
        evalRange(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);

    get addop => (plus  > _p.success((x, y) => x + y))
               | (minus > _p.success((x, y) => x - y));

    get mulop => (times > _p.success((x, y) => x * y))
               | (div   > _p.success((x, y) => x / y));
}


typedef String Converter(String decimal);


class ConvertEquation extends ParseEquation<String> {

    // Converters
    static String canonicalToLocal(String decimal)=>new Decimal(double.parse(decimal)).number;
    static String localToCanonical(String decimal)=>new Decimal.parse(decimal).canonical;
    static String passThrough(String decimal)=>decimal;

    Converter converter;
    ConvertEquation(this.converter, [RangeResolver resolver]): super(resolver);

    String call(String eq) {
        var result = parser.parse(eq.trim());
        if (result.startsWith('(') && result.endsWith(')'))
            return result.substring(1, result.length-1);
        return result;
    }

    String parseDecimal(sign, digits) =>
        converter(sign+digits.join());

    String parseRange(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, _p.PointedValue<String> end) =>
        resolver != null ?
            evalRange(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end).number :
            rangeToString(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);

    // supports localized format parsing
    get digits => _p.oneOf("1234567890., ") % 'digit';

    get addop => (plus  > _p.success((x, y) => "($x + $y)"))
               | (minus > _p.success((x, y) => "($x - $y)"));

    get mulop => (times > _p.success((x, y) => "($x * $y)"))
               | (div   > _p.success((x, y) => "($x / $y)"));
}
