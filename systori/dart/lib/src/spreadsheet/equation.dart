import 'package:parsers/parsers.dart';
import 'package:systori/decimal.dart';


Decimal solve(String equation) => Equation.parser.parse(equation.trim());


class Equation {

    static final Parser parser = new Equation().start;

    final Parser<String> digit = oneOf("1234567890.,") % 'digit';

    digits2decimal(digits) => new Decimal.parse(digits.join());

    lexeme(parser) => parser < spaces;
    token(str)     => lexeme(string(str));
    parens(parser) => parser.between(token('('), token(')'));

    get start => expr() < eof;

    get times  => token('*');
    get div    => token('/');
    get plus   => token('+');
    get minus  => token('-');
    get number => lexeme(digit.many1) ^ digits2decimal;

    expr() => rec(term).chainl1(addop);
    term() => rec(atom).chainl1(mulop);
    atom() => number | parens(rec(expr));

    get addop => (plus  > success((x, y) => x + y))
               | (minus > success((x, y) => x - y));

    get mulop => (times > success((x, y) => x * y))
               | (div   > success((x, y) => x / y));
}
