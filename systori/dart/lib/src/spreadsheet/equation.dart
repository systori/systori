import 'package:parsers/parsers.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';


class RangeResolver {

    int thisColumn;
    ColumnGetter getColumn;
    bool _collectRanges = true;
    bool get collectRanges => _collectRanges;
    set collectRanges(bool collect) {
        if (collect) {
            nextGroup = 0;
            ranges = [];
        }
        _collectRanges = collect;
    }

    int nextGroup = 0;
    List<Range> ranges = [];
    Map<String,RangeResult> results = {};

    reset() {
        results.values.forEach((r)=>r.reset());
        results.clear();
    }

    Decimal resolve(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end, startIdx, endIdx, src) {

        if (!collectRanges) {
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
        ranges.add(range);

        if (result.isEmpty) {
            var columnIdx = range.column != null ? range.column : thisColumn;
            range.calculate(getColumn(columnIdx));
        }

        return result.value;
    }
}


abstract class Equation {

    String get canonical;
    set canonical(String canonical);

    String get local;
    set local(String local);

    String get resolved;
    set resolved(String resolved);

    Decimal value;

    RangeResolver resolver = new RangeResolver();

    focus() {
        if (local == null || local.isEmpty)
            local = canonicalToLocal(canonical);
        return local;
    }

    changed(String change) {
        local = change;
        canonical = localToCanonical(local);
        resolver.collectRanges = true;
    }

    calculate(ColumnGetter getColumn, dependenciesChanged) {

        resolver.getColumn = getColumn;

        if (dependenciesChanged)
            resolver.reset();

        if (resolver.collectRanges) {
            resolved = localToResolved(local);
            resolver.collectRanges = false;
        }

        value = eval(canonical);

    }

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


abstract class ParseEquation<R> {

    Parser parser;
    RangeResolver resolver;
    ParseEquation(this.resolver) {
        parser = buildParser();
    }

    R call(String eq);
    R parseDecimal(sign, digits);
    R parseRange(PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, PointedValue<String> end);

    String rangeToString(PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, PointedValue<String> end) =>
        "${column.value}$direction$startEquation$start$startExclusive$colon$endExclusive$endEquation${end.value}";

    Decimal evalRange(PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, PointedValue<String> end) {
        var src = rangeToString(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);
        return resolver.resolve(
            column.value, direction,
            startEquation, start,
            startExclusive, colon, endExclusive,
            endEquation, end.value,
            column.position.offset, end.position.offset, src
        );
    }

    Parser<R> buildParser() => expr() < eof;

    lexeme(parser) => parser < spaces;
    token(str)     => lexeme(string(str));
    parens(parser) => parser.between(token('('), token(')'));

    get times  => token('*');
    get div    => token('/');
    get plus   => token('+');
    get minus  => token('-');

    get sign => (char('-') | char('+')).orElse('');
    get digits => oneOf("1234567890.") % 'digit';
    get decimal => (lexeme(sign) + digits.many1 ^ parseDecimal) % 'decimal';

    get range =>
            oneOf('ABC').orElse('').withPosition % 'column' +
            oneOf('@!') % 'direction' +
            char('&').orElse('') % 'equation symbol' +
            (digit.many1 ^ (s)=>s.join()).orElse('') % 'row' +
            char('[').orElse('') % 'exclusive range' +
            char(':').orElse('') % 'colon' +
            char(']').orElse('') % 'exclusive range' +
            char('&').orElse('') % 'equation symbol' +
            (digit.many1 ^ (s)=>s.join()).orElse('').withPosition % 'row'
            ^ parseRange;

    expr() => rec(term).chainl1(addop);
    term() => rec(atom).chainl1(mulop);
    atom() => lexeme(range) | lexeme(decimal) | parens(rec(expr));

    get addop => (plus  > success((x, y) => x + y))
               | (minus > success((x, y) => x - y));

    get mulop => (times > success((x, y) => x * y))
               | (div   > success((x, y) => x / y));
}


class EvaluateEquation extends ParseEquation<Decimal> {

    EvaluateEquation(resolver): super(resolver);

    Decimal call(String eq) => parser.parse(eq.trim());

    Decimal parseDecimal(sign, digits) => new Decimal.parse(sign+digits.join());

    Decimal parseRange(PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, PointedValue<String> end) =>
        evalRange(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);

    get addop => (plus  > success((x, y) => x + y))
               | (minus > success((x, y) => x - y));

    get mulop => (times > success((x, y) => x * y))
               | (div   > success((x, y) => x / y));
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

    String parseRange(PointedValue<String> column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, PointedValue<String> end) =>
        resolver != null ?
            evalRange(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end).number :
            rangeToString(column, direction, startEquation, start, startExclusive, colon, endExclusive, endEquation, end);

    // supports localized format parsing
    get digits => oneOf("1234567890., ") % 'digit';

    get addop => (plus  > success((x, y) => "($x + $y)"))
               | (minus > success((x, y) => "($x - $y)"));

    get mulop => (times > success((x, y) => "($x * $y)"))
               | (div   > success((x, y) => "($x / $y)"));
}
