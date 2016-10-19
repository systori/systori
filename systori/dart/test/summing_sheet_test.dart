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

    group("Range.sum()", () {

        int calc(String eq, List<int> ints, [hasEquation=-1]) {
            var equation = new Equation(eq);
            List<Equation> previous = [];
            ints.asMap().forEach((i, total) =>
                previous.add(new Equation(hasEquation==i ? '!' : '')..total=total)
            );
            return equation.ranges.first.sum(previous);
        }

        test("top-down summing, specific row", () {
            expect(calc('@', [1, 2, 4]), 1);
            expect(calc('@1', [1, 2, 4]), 1);
            expect(calc('@3', [1, 2, 4]), 4);
        });

        test("top-down summing, simple ranges", () {
            expect(calc('@:', [1, 2, 4]), 7);
            expect(calc('@1:', [1, 2, 4]), 7);
            expect(calc('@1:1', [1, 2, 4]), 1);
            expect(calc('@1:3', [1, 2, 4]), 7);
            expect(calc('@2:3', [1, 2, 4]), 6);
        });

        test("top-down summing, exclusive ranges", () {
            expect(calc('@]', [1, 2, 4, 5]), 7);
            expect(calc('@[', [1, 2, 4, 5]), 11);
            expect(calc('@[]', [1, 2, 4, 5]), 6);
            expect(calc('@2[', [1, 2, 4, 5]), 9);
            expect(calc('@]3', [1, 2, 4, 5]), 3);
        });

        test("top-down summing, equation stops, simple", () {
            expect(calc('@&', [1, 2, 4, 5]), 0);
            expect(calc('@&', [1, 2, 4, 5], 0), 1);
            expect(calc('@&', [1, 2, 4, 5], 3), 5);
        });

        test("top-down summing, equation stops, range", () {
            expect(calc('@&:', [1, 2, 4, 5]), 0);
            expect(calc('@&:', [1, 2, 4, 5], 0), 12);
            expect(calc('@&:', [1, 2, 4, 5], 2), 9);
            expect(calc('@:&', [1, 2, 4, 5], 2), 7);
            expect(calc('@]&', [1, 2, 4, 5], 2), 3);
            expect(calc('@1:]&', [1, 2, 4, 5], 2), 3);
        });

        test("bottom-up summing, specific row", () {
            expect(calc('!', [1, 2, 4]), 4);
            expect(calc('!1', [1, 2, 4]), 4);
            expect(calc('!3', [1, 2, 4]), 1);
        });

        test("bottom-up summing, simple ranges", () {
            expect(calc('!:', [1, 2, 4]), 7);
            expect(calc('!1:', [1, 2, 4]), 7);
            expect(calc('!1:1', [1, 2, 4]), 4);
            expect(calc('!1:3', [1, 2, 4]), 7);
            expect(calc('!2:3', [1, 2, 4]), 3);
        });

        test("bottom-up summing, equation stops, range", () {
            expect(calc('!&:', [1, 2, 4, 5]), 0);
            expect(calc('!&:', [1, 2, 4, 5], 3), 12);
            expect(calc('!&:', [1, 2, 4, 5], 2), 7);
            expect(calc('!:&', [1, 2, 4, 5], 2), 9);
            expect(calc('!]&', [1, 2, 4, 5], 2), 5);
            expect(calc('!1:]&', [1, 2, 4, 5], 2), 5);
        });

    });

    group("Range.startIdx/endIdx", () {

        List<int> calc(String eq, List<int> ints, [hasEquation = -1]) {
            var equation = new Equation(eq);
            List<Equation> previous = [];
            ints.asMap().forEach((i, total) =>
                previous.add(
                    new Equation(hasEquation == i ? '!' : '')..total = total)
            );
            var range = equation.ranges.first;
            range.sum(previous);
            return [range.startIdx, range.endIdx];
        }

        test("top-down, no range", () {
            expect(calc('@', [1, 2, 4]), [0, 0]);
            expect(calc('@1', [1, 2, 4]), [0, 0]);
            expect(calc('@3', [1, 2, 4]), [2, 2]);
        });

        test("top-down, with range", () {
            expect(calc('@:3', [1, 2, 4]), [0, 2]);
            expect(calc('@:1', [1, 2, 4]), [0, 0]);
            expect(calc('@1:', [1, 2, 4]), [0, 2]);
            expect(calc('@3:', [1, 2, 4]), [2, 2]);
            expect(calc('@2:', [1, 2, 4]), [1, 2]);
        });

        test("bottom-up, no range", () {
            expect(calc('!', [1, 2, 4]), [2, 2]);
            expect(calc('!1', [1, 2, 4]), [2, 2]);
            expect(calc('!3', [1, 2, 4]), [0, 0]);
        });

        test("bottom-up, with range", () {
            expect(calc('!:3', [1, 2, 4]), [0, 2]);
            expect(calc('!:1', [1, 2, 4]), [2, 2]);
            expect(calc('!1:', [1, 2, 4]), [0, 2]);
            expect(calc('!3:', [1, 2, 4]), [0, 0]);
            expect(calc('!2:', [1, 2, 4]), [0, 1]);
        });
    });

    group("Equation.calculate() without ranges", () {

        Equation calc(int qty, String eq, int price) =>
            new Equation(eq)..calculate(qty, price, []);

        test("basic", () {
            expect(calc(200, '', 300).total, 600);
            expect(calc(200, 'm2', 500).total, 1000);
        });

        test("percent", () {
            expect(calc(20, '', 1200).total, 240);
            expect(calc(2000, '%', 1200).total, 240);
        });

    });

    group("Equation.calculate() with ranges", () {

        int calc(int qty, String eq, List<int> ints, [hasEquation=-1]) {
            var equation = new Equation(eq);
            List<Equation> previous = [];
            ints.asMap().forEach((i, total) =>
                previous.add(new Equation(hasEquation==i ? '!' : '')..total=total*100)
            );
            return (equation.calculate(qty*100, null, previous)/100).round();
        }

        test("single number ranges", () {
            expect(calc(1, '!!!', [1,2]), 6);
            expect(calc(1, '!2!2!2', [1,2]), 3);
            expect(calc(1, '@@@', [1,2]), 3);
            expect(calc(1, '@2@2@2', [1,2]), 6);
        });

        test("ranges, bottom-up", () {
            expect(calc(1, '!2:4!5:', [1,2,3,4,5,6]), equals(15));
            expect(calc(1, '!:3!5:', [1,2,3,4,5,6]), equals(18));
            expect(calc(1, '!:2!4', [1,2,3,4,5,6]), equals(14));
        });

        test("ranges, top-down", () {
            expect(calc(1, '@2:4@5:', [1,2,3,4,5,6]), equals(20));
            expect(calc(1, '@:3@5:', [1,2,3,4,5,6]), equals(17));
            expect(calc(1, '@:2@4', [1,2,3,4,5,6]), equals(7));
        });

        test("ranges, mixed", () {
            expect(calc(1, '@:2!:2', [1,2,3,4,5,6]), equals(14));
            expect(calc(1, '@:3!:3', [1,2,3,4,5,6]), equals(21));
            expect(calc(1, '@:!:', [1,2,3,4,5,6]), equals(42));
        });

    });

    group("Equation.rowColors", () {
        List<int> calc(String eq, List<int> ints) {
            var equation = new Equation(eq);
            List<Equation> previous = [];
            ints.asMap().forEach((i, total) =>
                previous.add(new Equation('')..total = total * 100)
            );
            equation.calculate(0, null, previous);
            return equation.rowColors;
        }

        test("single number non-ranges", () {
            expect(calc('!', [1,2,3]), [0,0,1]);
            expect(calc('!@', [1,2,3]), [2,0,1]);
            expect(calc('!!@', [1,2,3]), [3,0,-1]);
        });

        test("multiple ranges", () {
            expect(calc('!:', [1,2,3]), [1,1,1]);
            expect(calc('!:@', [1,2,3]), [-1,1,1]);
            expect(calc('!!@:', [1,2,3]), [3,3,-1]);
        });

    });

    group("Row.calculate()", () {

        test("basic calculations", () {
            calc(q,u,p) => new Row(q,u,p).calculate([]).total;
            expect(calc('', '', ''), equals(0));
            expect(calc('5', '', ''), equals(0));
            expect(calc('0', '', '5'), equals(0));
            expect(calc('', '', '5'), equals(500));
            expect(calc('5', '', '5'), equals(2500));
            expect(calc('5', 'm', '5'), equals(2500));
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
                new Row('50', '%!:', ''),  // 50% of 20 = 10
            ]);
            expect(sheet.calculate(), equals(3000));

            sheet = new Sheet([
                new Row('1', 'm', '7'),
                new Row('1', 'm', '7'),
                new Row('2', 'm', '3'),
                new Row('50', '%!', ''),  // 50% of 6 = 3
            ]);
            expect(sheet.calculate(), equals(2300));

            sheet = new Sheet([
                new Row('1', 'm', '7'),
                new Row('1', 'm', '7'),
                new Row('2', 'm', '3'),
                new Row('2', '!:3', ''),  // 2 * sum = 40
            ]);
            expect(sheet.calculate(), equals(6000));

            sheet = new Sheet([
                new Row('1', 'm', '7'), //               7.00
                new Row('1', 'm', '7'), //               7.00
                new Row('10', '%!:', ''), // 10% of 14 = 1.40
                new Row('2', 'm', '3'), //               6.00
                new Row('2', '!:2', ''), // 2* (1.4+6) = 14.80
            ]);
            expect(sheet.calculate(), equals(3620));

        });

    });
}