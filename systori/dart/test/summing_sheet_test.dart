import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:systori/common.dart';
import 'package:systori/summing_sheet.dart';

class Sheet extends SummingSheet {
    List<SummingRow> rows;
    Sheet(this.rows);
}

class Row extends SummingRow {
    var total, isPriceCalculated;
    var qty, unit, price;
    Row(this.qty, this.unit, this.price);
}

main() async {
    Intl.systemLocale = 'de';

    group("currency parsing", () {

        tearDown(() {
            Intl.withLocale('de', ()=> CURRENCY = make_currency_format());
        });

        test("german amounts", () {
            expect(string_to_int(''), equals(null));
            expect(string_to_int('0'), equals(0));
            expect(string_to_int('1'), equals(100));
            expect(string_to_int('1,00'), equals(100));
            expect(string_to_int('1.000,00'), equals(100000));
        });

        test("american amounts", () {
            Intl.withLocale('en', ()=> CURRENCY = make_currency_format());
            expect(string_to_int(''), equals(null));
            expect(string_to_int('0'), equals(0));
            expect(string_to_int('1'), equals(100));
            expect(string_to_int('1.00'), equals(100));
            expect(string_to_int('1,000.00'), equals(100000));
        });
    });

    group("equation calculator", () {

        int calc(String eq, List<int> ints) => new Equation(eq).calculate(ints);

        test("isSum, isSumAll", () {
            expect(new Equation('%').isSum, isTrue);
            expect(new Equation('!').isSum, isTrue);
            expect(new Equation('!8').isSum, isTrue);
            expect(new Equation('!!').isSum, isTrue);
            expect(new Equation('8').isSum, isFalse);
            expect(new Equation('m2').isSum, isFalse);
            expect(new Equation('%').isSumAll, isFalse);
            expect(new Equation('!').isSumAll, isFalse);
            expect(new Equation('!7').isSumAll, isFalse);
            expect(new Equation('!!').isSumAll, isTrue);
        });

        test("sumX", () {
            expect(new Equation('!').sumX, equals(1));
            expect(new Equation('!-9').sumX, equals(1));
            expect(new Equation('!0').sumX, equals(0));
            expect(new Equation('!99').sumX, equals(99));
            expect(new Equation('%').sumX, equals(1));
            expect(new Equation('%0').sumX, equals(0));
            expect(new Equation('%99').sumX, equals(99));

            var eq = new Equation('!!');
            expect(eq.sumX, equals(1));
            eq.calculate([1,2,3,4,5]);
            expect(eq.sumX, equals(5));

            eq = new Equation('%5');
            expect(eq.sumX, equals(5));
            eq.calculate([1,2]);
            expect(eq.sumX, equals(2));
        });

        test("not an equation", () {
            expect(calc('', [5, 4]), isNull);
            expect(calc('m2', [5, 4]), isNull);
        });

        test("zero result with no previous rows", () {
            expect(calc('%', []), equals(0));
            expect(calc('%!', []), equals(0));
            expect(calc('%3', []), equals(0));
            expect(calc('!', []), equals(0));
            expect(calc('!2', []), equals(0));
            expect(calc('!!', []), equals(0));
        });

        test("simple sum", () {
            expect(calc('!!', [1,2,3,4]), equals(10));
            expect(calc('!2', [1,2,3,4]), equals(7));
            expect(calc('%2', [1,2,3,4]), equals(7));
            expect(calc('!9', [1,2,3,4]), equals(10));
        });

    });

    group("summing row", () {

        test("basic calculations", () {
            calc(q,u,p) => new Row(q,u,p).calculate([]);
            expect(calc('', '', ''), equals(0));
            expect(calc('5', '', ''), equals(0));
            expect(calc('0', '', '5'), equals(0));
            expect(calc('', '', '5'), equals(500));
            expect(calc('5', '', '5'), equals(2500));
            expect(calc('5', 'm', '5'), equals(2500));
        });

        test("summing calculations", () {
            calc(q,u,p) => new Row(q,u,p).calculate([7,7]);

            expect(calc('', '', ''), equals(0));
            expect(calc('', '!', ''), equals(7));
            expect(calc('', '!2', ''), equals(14));
            expect(calc('', '!!', ''), equals(14));

            expect(calc('', '%', ''), equals(0));
            expect(calc('', '%2', ''), equals(0));
            expect(calc('100', '%', ''), equals(7));
            expect(calc('100', '%2', ''), equals(14));
        });

    });

    group("Summing Sheet", () {

        var sheet;

        test("simple calculations", () {

            sheet = new Sheet([]);
            expect(sheet.calculate(), equals(0));

            sheet = new Sheet([new Row('1', 'm', '1')]);
            expect(sheet.calculate(), equals(100));

            sheet = new Sheet([
                new Row('1', 'm', '7'),
                new Row('1', 'm', '7'),
                new Row('2', 'm', '3'),
                new Row('50', '%!!', ''),  // 50% of 20 = 10
            ]);
            expect(sheet.calculate(), equals(3000));

            sheet = new Sheet([
                new Row('1', 'm', '7'),
                new Row('1', 'm', '7'),
                new Row('2', 'm', '3'),
                new Row('50', '%', ''),  // 50% of 6 = 3
            ]);
            expect(sheet.calculate(), equals(2300));

            sheet = new Sheet([
                new Row('1', 'm', '7'),
                new Row('1', 'm', '7'),
                new Row('2', 'm', '3'),
                new Row('2', '!3', ''),  // 2 * sum = 40
            ]);
            expect(sheet.calculate(), equals(6000));

            sheet = new Sheet([
                new Row('1', 'm', '7'), //               7.00
                new Row('1', 'm', '7'), //               7.00
                new Row('10', '%!!', ''), // 10% of 14 = 1.40
                new Row('2', 'm', '3'), //               6.00
                new Row('2', '!2', ''), // 2* (1.4+6) = 14.80
            ]);
            expect(sheet.calculate(), equals(3620));

        });

    });
}