import 'package:systori/numbers.dart';
import 'package:parsers/parsers.dart' as _p;


typedef List<Cell> ColumnGetter(int columnIdx);


format(int column, Decimal decimal) {
    if (column == 1 || column == 2) {
        return decimal.money;
    } else { // column == 0
        return decimal.number;
    }
}


abstract class Cell {

    String get text;
    set text(String text);

    String get canonical;
    set canonical(String canonical);

    String get local;
    set local(String local);

    String get resolved;
    set resolved(String resolved);

    String get preview;
    set preview(String preview);

    int row;
    int column;

    Decimal value;

    RangeResolver resolver = new RangeResolver();

    static final RegExp ZERO = new RegExp(r"^-?[0.,]*$");
    static final RegExp NUMBER = new RegExp(r"^-?[0-9., ]+$");
    bool _isBlankOrZero(String txt) => txt.isEmpty || ZERO.hasMatch(txt);
    bool get isCanonicalBlank => _isBlankOrZero(canonical.trim());
    bool get isCanonicalNotBlank => !isCanonicalBlank;
    bool get isCanonicalNumber => NUMBER.hasMatch(canonical.trim());
    bool get isCanonicalEquation => isCanonicalNotBlank && !isCanonicalNumber;
    bool get isTextBlank => _isBlankOrZero(text.trim());
    bool get isTextNotBlank => !isTextBlank;
    bool get isTextNumber => NUMBER.hasMatch(text.trim());
    bool get isTextEquation => isTextNotBlank && !isTextNumber;

    String _previous_text;
    bool get isChanged => _previous_text != null && text != _previous_text;
    bool get isFocused; // document.activeElement == this

    focused() {

        if (value == null) {
            value = isTextNumber ? new Decimal.parse(text, 3) : new Decimal(null, 3);
        }

        if (isCanonicalBlank) {
            if (isTextNumber) {
                if (value == null) {
                    value = new Decimal.parse(text, 3);
                }
                preview = format(column, value);
            }
            text = "";
        } else if (isCanonicalEquation) {
            if (local == "") {
                local = canonicalToLocal(canonical);
                resolved = ""; // need to trigger parsing to get new range locations
            }
            text = local;
        }
        _previous_text = text;
    }

    blurred() {
        text = value.isNonzero ? format(column, value) : "";
        _previous_text = null;
    }

    _set_preview() {
        if (isCanonicalEquation) {
            if (resolved != value.number) {
                preview = "${resolved} = ${format(column, value)}";
            } else {
                preview = format(column, value);
            }
        } else {
            preview = "";
        }
    }

    clear() => setManual(new Decimal(null, 3));

    setManual(Decimal decimal) {
        value = decimal;
        _previous_text = text = preview = decimal.isNonzero ? format(column, decimal) : "";
        canonical = decimal.canonical;
        local = resolved = preview = '';
    }

    setCalculated(Decimal decimal) {
        value = decimal;
        preview = value.isNonzero ? format(column, decimal) : "";
        if (!isFocused) {
            _previous_text = text = preview;
        }
    }

    calculate(ColumnGetter getColumn, [bool dependenciesChanged=false]) {

        resolver.thisColumn = column;
        resolver.getColumn = getColumn;

        if (value == null) {
            value = isTextNumber ? new Decimal.parse(text, 3) : new Decimal(null, 3);
        }

        if (isFocused) {

            if (isChanged) {

                local = "";

                if (isTextEquation) {

                    var _old_canonical = canonical;
                    try {
                        canonical = localToCanonical(text);
                        resolver.withCollectRanges(() {
                            resolved = localToResolved(text);
                        });
                        value = eval(canonical);
                        _set_preview();
                    } catch(e) {
                        canonical = _old_canonical;
                        resolver.withCollectRanges(() {
                            resolved = "";
                        });
                        value = new Decimal(0, 3);
                        preview = e.substring(8);
                    }

                } else {

                    value = new Decimal.parse(text, 3);
                    canonical = value.canonical;
                    resolved = "";
                    preview = "";

                }

            } else {

                if (isTextEquation && resolved == "") {
                    try {
                        resolver.withCollectRanges(() {
                            resolved = localToResolved(text);
                        });
                        _set_preview();
                    } catch(e) {
                        resolved = "";
                        preview = "";
                    }
                }

            }

        } else if (dependenciesChanged) {

            if (isCanonicalEquation) {

                resolver.withCleanCache(() {
                    value = eval(canonical);
                });
                text = format(column, value);

                if (local != "") {
                    if (resolved != "") {
                        resolved = localToResolved(local);
                    }
                    _set_preview();
                }

            }

        }

        _previous_text = text;

    }

    ConvertEquation _canonicalToLocal;
    ConvertEquation get canonicalToLocal {
        if (_canonicalToLocal == null)
            _canonicalToLocal = newCanonicalToLocal();
        return _canonicalToLocal;
    }
    newCanonicalToLocal() => new ConvertEquation(ConvertEquation.canonicalToLocal);

    ConvertEquation _localToCanonical;
    ConvertEquation get localToCanonical {
        if (_localToCanonical == null)
            _localToCanonical = newLocalToCanonical();
        return _localToCanonical;
    }
    newLocalToCanonical() => new ConvertEquation(ConvertEquation.localToCanonical);

    ConvertEquation _localToResolved;
    ConvertEquation get localToResolved {
        if (_localToResolved == null)
            _localToResolved = newLocalToResolved();
        return _localToResolved;
    }
    newLocalToResolved() => new ConvertEquation(ConvertEquation.localToLocal, resolver);

    EvaluateEquation _eval;
    EvaluateEquation get eval {
        if (_eval == null)
            _eval = newEval();
        return _eval;
    }
    newEval() => new EvaluateEquation(resolver);

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
        value = new Decimal(0, 3);
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

        if (cells.current.isCanonicalEquation) equationIdx++;

        if ((!isStartEquation && start == i) ||
            (isStartEquation && cells.current.isCanonicalEquation && start == equationIdx)) {
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
            (isEndEquation && cells.current.isCanonicalEquation && end == equationIdx) ||
            lastIdx == i) {
            // last row means we're not inside anymore
            inside = false;
            if (isEndExclusive)
                // if we're at the end and ] then don't add this row, break immediately
                break;
            if (lastIdx == i && isEndEquation && (!cells.current.isCanonicalEquation || end != equationIdx)) {
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

    int nextGroup = 1;
    List<Range> ranges = [];
    Map<String,RangeResult> results = {};

    withCleanCache(Function iterate()) {
        nextGroup = 1;
        results.values.forEach((r)=>r.reset());
        results = {};
        withCollectRanges(iterate);
    }

    bool _collectRanges = false;
    withCollectRanges(Function iterate()) {
        ranges = [];
        _collectRanges = true;
        iterate();
        _collectRanges = false;
    }

    Decimal resolve(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end, startIdx, endIdx, src) {

        if (results.containsKey(src) && !_collectRanges) {
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

        if (_collectRanges)
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
    R parseRange(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);

    String rangeToString(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end) =>
        "${column.value}$direction$startEquation$start$startExclusive$colon$endExclusive$endEquation$end";

    Decimal evalRange(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end) {
        var src = rangeToString(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);
        return resolver.resolve(
            column.value, direction,
            startEquation, start,
            startExclusive, colon, endExclusive,
            endEquation, end,
            column.position.offset, column.position.offset+src.length, src
        );
    }

    _p.Parser<R> buildParser() => expr() < (_p.eof as _p.Parser<R>);

    static final _spaces = " \u{00a0}\t\n\r\v\f";
    static final _p.Parser<String> space = _p.oneOf(_spaces) % 'space';
    final _p.Parser<R> spaces = ((space.many > _p.success(null)) % 'spaces') as _p.Parser<R>;

    _p.Parser<R> lexeme(_p.Parser<R> parser) => parser < spaces;
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
           (_p.oneOf('ABC').orElse('').withPosition % 'column ABC' +
            _p.oneOf('@!') % '@ or !' +
            _p.char('&').orElse('') % '&' +
            (_p.digit.many1 ^ (s)=>s.join()).orElse('') % 'a row number' +
            _p.char('[').orElse('') % '[' +
            _p.char(':').orElse('') % ':' +
            _p.char(']').orElse('') % ']' +
            _p.char('&').orElse('') % '&' +
            (_p.digit.many1 ^ (s)=>s.join()).orElse('') % 'a row number'
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

    Decimal parseDecimal(sign, digits) => new Decimal(double.parse(sign+digits.join()), 3);

    Decimal parseRange(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end) =>
        evalRange(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);

    get addop => (plus  > _p.success((x, y) => x + y))
               | (minus > _p.success((x, y) => x - y));

    get mulop => (times > _p.success((x, y) => x * y))
               | (div   > _p.success((x, y) => x / y));
}


typedef String Converter(String decimal);


class ConvertEquation extends ParseEquation<String> {

    // Converters
    static String canonicalToLocal(String decimal)=>new Decimal(double.parse(decimal), 3).number;
    static String localToCanonical(String decimal)=>new Decimal.parse(decimal, 3).canonical;
    static String localToLocal(String decimal)=>new Decimal.parse(decimal, 3).number;
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

    String parseRange(_p.PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end) =>
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
