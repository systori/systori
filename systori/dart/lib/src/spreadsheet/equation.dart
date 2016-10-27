import 'package:parsers/parsers.dart';
import 'package:systori/decimal.dart';


abstract class ParseEquation<R> {

    parseDecimal(sign, digits);
    parseRange(column, direction, start, startExclusive, colon, endExclusive, end);

    get equation => expr() < eof;

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
            oneOf('ABC').orElse('') % 'column' +
            oneOf('@!') % 'direction' +
            ((digit.many1 ^ (s)=>s.join()) | char('&')).orElse('') % 'start row' +
            char('[').orElse('') % 'start row' +
            char(':').orElse('') % 'colon' +
            char(']').orElse('') % 'end row' +
            ((digit.many1 ^ (s)=>s.join()) | char('&')).orElse('') % 'end row'
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

    static final solve = new EvaluateEquation();

    Parser _parser;
    EvaluateEquation() {
        _parser = equation;
    }

    Decimal call(String eq) => _parser.parse(eq.trim());

    parseDecimal(sign, digits) =>
        new Decimal.parse(sign+digits.join());

    parseRange(column, direction, start, startExclusive, colon, endExclusive, end) =>
        new Decimal(2);

    get addop => (plus  > success((x, y) => x + y))
               | (minus > success((x, y) => x - y));

    get mulop => (times > success((x, y) => x * y))
               | (div   > success((x, y) => x / y));
}


class ConvertEquation extends ParseEquation<String> {

    static final canonicalToLocal = new ConvertEquation(
        (decimal) => new Decimal(double.parse(decimal)).number);

    static final localToCanonical = new ConvertEquation(
        (decimal) => new Decimal.parse(decimal).canonical);

    Parser _parser;
    Function converter;

    ConvertEquation(this.converter) {
        _parser = equation;
    }

    parseDecimal(sign, digits) =>
        converter(sign+digits.join());

    parseRange(column, direction, start, startExclusive, colon, endExclusive, end) =>
        "$column$direction$start$startExclusive$colon$endExclusive$end";

    String call(String eq) {
        var result = _parser.parse(eq.trim());
        if (result.startsWith('(') && result.endsWith(')'))
            return result.substring(1, result.length-1);
        return result;
    }

    // supports space delimited thousands
    get digits => oneOf("1234567890., ") % 'digit';

    get addop => (plus  > success((x, y) => "($x + $y)"))
               | (minus > success((x, y) => "($x - $y)"));

    get mulop => (times > success((x, y) => "($x * $y)"))
               | (div   > success((x, y) => "($x / $y)"));
}
