@TestOn('vm')
import 'package:test/test.dart';
import 'package:intl/intl.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/numbers.dart';
import 'package:systori/spreadsheet.dart';


class TestCell extends Cell {

    String text = "";
    String canonical = "";
    String local = "";
    String resolved = "";
    String preview = "";

    TestCell([_text="", _canonical="", _col=0, _row=0])
    {this.text=_text; this.canonical=_canonical; this.column=_col; this.row=_row;}

    bool isFocused = false; // real implementation uses document.activeElement == this

    @override
    focused() {
        isFocused = true;
        super.focused();
    }

    @override
    blurred() {
        isFocused = false;
        super.blurred();
    }

    int canonicalToLocalAccessed = 0;
    @override
    ConvertEquation get canonicalToLocal {
        canonicalToLocalAccessed++;
        return super.canonicalToLocal;
    }
    int canonicalToLocalCreated = 0;
    @override
    newCanonicalToLocal() {
        canonicalToLocalCreated++;
        return super.newCanonicalToLocal();
    }

    int localToCanonicalAccessed = 0;
    @override
    ConvertEquation get localToCanonical {
        localToCanonicalAccessed++;
        return super.localToCanonical;
    }
    int localToCanonicalCreated = 0;
    @override
    newLocalToCanonical() {
        localToCanonicalCreated++;
        return super.newLocalToCanonical();
    }

    int localToResolvedAccessed = 0;
    @override
    ConvertEquation get localToResolved {
        localToResolvedAccessed++;
        return super.localToResolved;
    }
    int localToResolvedCreated = 0;
    @override
    newLocalToResolved() {
        localToResolvedCreated++;
        return super.newLocalToResolved();
    }

    int evalAccessed = 0;
    @override
    EvaluateEquation get eval {
        evalAccessed++;
        return super.eval;
    }
    int evalCreated = 0;
    @override
    newEval() {
        evalCreated++;
        return super.newEval();
    }

}


// Cell helpers

Cell cell([String txt='', String canonical='', _col=0, _row=0]) =>
    new TestCell(txt, canonical, _col, _row);

List<Cell> cells(List<String> values, [eq1=-1, eq2=-1]) =>
    enumerate<String>(values).
    map((total) => cell(total.value, eq1==total.index||eq2==total.index ? '!' : '')..value=new Decimal.parse(total.value)).
    toList();

ColumnGetter getColumnReturns(List<String> values, [eq1=-1, eq2=-1]) =>
    (col) => cells(values, eq1, eq2);

Cell eval(String eq, List<int> values, [eq1=-1, eq2=-1]) =>
    cell('', eq, 0, values.length)..calculate(getColumnReturns(values.map((v)=>v.toString()).toList(), eq1, eq2), true);

double cellTotal(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    eval(eq, ints!=null?ints:[], eq1, eq2).value.decimal;

// Range helpers

List<Range> ranges(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    eval(eq, ints!=null?ints:[], eq1, eq2).resolver.ranges;

Range range(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    ranges(eq, ints, eq1, eq2).first;

List index(String eq, List<int> ints, [eq1=-1, eq2=-1]) {
    var _range = range(eq, ints, eq1, eq2);
    return [_range.result.start, _range.result.end];
}

List groups(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    eval(eq, ints!=null?ints:[], eq1, eq2).resolver.results.values.map((r)=>r.group).toList();

List rangeGroups(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    eval(eq, ints!=null?ints:[], eq1, eq2).resolver.ranges.map((r)=>r.result.group).toList();

double rangeTotal(String eq, [List<int> ints, eq1=-1, eq2=-1]) =>
    range(eq, ints, eq1, eq2).result.value.decimal;

List srcIdx(String eq, [List<int> ints, eq1=-1, eq2=-1]) {
    var _range = range(eq, ints, eq1, eq2);
    return [_range.srcStart, _range.srcEnd];
}

main() {

    group("Conversion", () {

        canonical(String equation) => cell().localToCanonical(equation);
        local(String equation) => cell().canonicalToLocal(equation);
        resolve(String equation, List<String> values) =>
            (cell('', '', 0, values.length)..resolver.getColumn = getColumnReturns(values))
            .localToResolved(equation);

        test("locale: de", () {
            Intl.withLocale("de", ()=> Decimal.updateFormats());

            expect(canonical("2-1 000,01"), "2 - 1000.01");
            expect(canonical("2-1.000,01"), "2 - 1000.01");
            expect(canonical("2--1.000,01"), "2 - -1000.01");
            expect(canonical("2--1.000,01+A!"), "(2 - -1000.01) + A!");

            expect(local("2 - 1000.01"), "2 - 1.000,01");
            expect(local("2 - -1000.01"), "2 - -1.000,01");

            expect(resolve("2--1.000,01+A!", ['99']), "(2 - -1.000,01) + 99");

            // regression test from 01/12/2017
            // EvaluateEquation.parseDecimal was using localized parser on
            // canonical values, resulting in 1.1 being parsed as 11
            expect(cellTotal("18 * 1.1"), 19.8);
        });

        test("locale: en", () {
            Intl.withLocale("en", ()=> Decimal.updateFormats());

            expect(canonical("2-1 000.01"), "2 - 1000.01");
            expect(canonical("2-1,000.01"), "2 - 1000.01");
            expect(canonical("2--1,000.01"), "2 - -1000.01");
            expect(canonical("2--1,000.01+A@1:&"), "(2 - -1000.01) + A@1:&");
            expect(canonical("\u{00a0}A!\u{00a0}+\u{00a0}B!:\u{00a0}"), "A! + B!:");

            expect(local("2 - 1000.01"), "2 - 1,000.01");
            expect(local("2 - -1000.01"), "2 - -1,000.01");

            expect(resolve("2--1,000.01+A@1:", ['99']), "(2 - -1,000.01) + 99");
        });

        tearDown(() {
            Intl.withLocale('en', ()=> Decimal.updateFormats());
        });

    });

    group("Range parsing", () {

        test("many ranges", () {
            expect(ranges('1+1').length, 0);
            expect(ranges('(1+1)-A@7').length, 1);
            expect(ranges('(1+!&*(1/!))-A@7', [1]).length, 3);
        });

        test("column", () {
            expect(range('@').column, null);
            expect(range('A@').column, 0);
            expect(range('C@').column, 2);
        });

        test("start/isStartEquation", () {
            expect(range('@').start, 1);
            expect(range('@4').start, 4);
            expect(range('@99:').start, 99);
            expect(range('@').isStartEquation, false);
            expect(range('@&').isStartEquation, true);
        });

        test("end/isEndEquation", () {
            expect(range('@').end, null);
            expect(range('@4:').end, null);
            expect(range('@9:9').end, 9);
            expect(range('@').isEndEquation, false);
            expect(range('@:&').isEndEquation, true);
        });

        test("startIdx/endIdx", () {
            expect(srcIdx('@'), [0, 1]);
            expect(srcIdx('@9:'), [0, 3]);
            expect(srcIdx('1+((@2:&1*2)+!)'), [4, 9]);
        });

    });

    group("Range.calculate()", () {

        test("top-down summing, specific row", () {
            expect(rangeTotal('@', [1, 2, 4]), 1);
            expect(rangeTotal('@1', [1, 2, 4]), 1);
            expect(rangeTotal('@3', [1, 2, 4]), 4);
        });

        test("bottom-up summing, specific row", () {
            expect(rangeTotal('!', [1, 2, 4]), 4);
            expect(rangeTotal('!1', [1, 2, 4]), 4);
            expect(rangeTotal('!3', [1, 2, 4]), 1);
        });

        test("top-down summing, simple ranges", () {
            expect(rangeTotal('@:', [1, 2, 4]), 7);
            expect(rangeTotal('@1:', [1, 2, 4]), 7);
            expect(rangeTotal('@1:1', [1, 2, 4]), 1);
            expect(rangeTotal('@1:3', [1, 2, 4]), 7);
            expect(rangeTotal('@2:3', [1, 2, 4]), 6);
        });

        test("bottom-up summing, simple ranges", () {
            expect(rangeTotal('!:', [1, 2, 4]), 7);
            expect(rangeTotal('!1:', [1, 2, 4]), 7);
            expect(rangeTotal('!1:1', [1, 2, 4]), 4);
            expect(rangeTotal('!1:3', [1, 2, 4]), 7);
            expect(rangeTotal('!2:3', [1, 2, 4]), 3);
        });

        test("top-down summing, exclusive ranges", () {
            expect(rangeTotal('@]', [1, 2, 4, 5]), 7);
            expect(rangeTotal('@[', [1, 2, 4, 5]), 11);
            expect(rangeTotal('@[]', [1, 2, 4, 5]), 6);
            expect(rangeTotal('@2[', [1, 2, 4, 5]), 9);
            expect(rangeTotal('@]3', [1, 2, 4, 5]), 3);
        });

        test("bottom-up summing, exclusive ranges", () {
            expect(rangeTotal('!]', [1, 2, 4, 5]), 11);
            expect(rangeTotal('![', [1, 2, 4, 5]), 7);
            expect(rangeTotal('![]', [1, 2, 4, 5]), 6);
            expect(rangeTotal('!2[', [1, 2, 4, 5]), 3);
            expect(rangeTotal('!]3', [1, 2, 4, 5]), 9);
        });

        test("top-down summing, equation stops, simple", () {
            expect(rangeTotal('@&', [1, 2, 4, 5]), 0);
            expect(rangeTotal('@&', [1, 2, 4, 5], 0), 1);
            expect(rangeTotal('@&', [1, 2, 4, 5], 3), 5);
        });

        test("bottom-up summing, equation stops, simple", () {
            expect(rangeTotal('!&', [1, 2, 4, 5]), 0);
            expect(rangeTotal('!&', [1, 2, 4, 5], 0), 1);
            expect(rangeTotal('!&', [1, 2, 4, 5], 3), 5);
        });

        test("top-down summing, specific equation stops, simple", () {
            expect(rangeTotal('@&', [1, 2, 4, 5], 1, 3), 2);
            expect(rangeTotal('@&1', [1, 2, 4, 5], 1, 3), 2);
            expect(rangeTotal('@&2', [1, 2, 4, 5], 1, 3), 5);
        });

        test("bottom-up summing, specific equation stops, simple", () {
            expect(rangeTotal('!&', [1, 2, 4, 5], 1, 3), 5);
            expect(rangeTotal('!&1', [1, 2, 4, 5], 1, 3), 5);
            expect(rangeTotal('!&2', [1, 2, 4, 5], 1, 3), 2);
        });

        test("top-down summing, equation stops, range", () {
            expect(rangeTotal('@&:', [1, 2, 4, 5]), 0);
            expect(rangeTotal('@&:', [1, 2, 4, 5], 0), 12);
            expect(rangeTotal('@&:', [1, 2, 4, 5], 2), 9);
            expect(rangeTotal('@:&', [1, 2, 4, 5], 2), 7);
            expect(rangeTotal('@]&', [1, 2, 4, 5], 2), 3);
            expect(rangeTotal('@1:]&', [1, 2, 4, 5], 2), 3);
        });

        test("bottom-up summing, equation stops, range", () {
            expect(rangeTotal('!&:', [1, 2, 4, 5]), 0);
            expect(rangeTotal('!:&', [1, 2, 4, 5]), 0);
            expect(rangeTotal('!&:&', [1, 2, 4, 5]), 0);
            expect(rangeTotal('!&:', [1, 2, 4, 5], 3), 12);
            expect(rangeTotal('!&:', [1, 2, 4, 5], 2), 7);
            expect(rangeTotal('!:&', [1, 2, 4, 5], 2), 9);
            expect(rangeTotal('!]&', [1, 2, 4, 5], 2), 5);
            expect(rangeTotal('!1:]&', [1, 2, 4, 5], 2), 5);
        });

        test("top-down summing, specific equation stops, range", () {
            expect(rangeTotal('@&:&2', [1, 2, 4, 5], 1, 3), 11);
            expect(rangeTotal('@&2:', [1, 2, 4, 5], 0, 2), 9);
        });

        test("bottom-up summing, specific equation stops, range", () {
            expect(rangeTotal('!&:&2', [1, 2, 4, 5], 1, 3), 11);
            expect(rangeTotal('!&2:', [1, 2, 4, 5], 1, 2), 3);
        });

    });

    group("RangeResult.group", () {

        test("result.group", () {
            expect(groups('@'), [1]);
            expect(groups('@+!'), [1,2]);
            expect(groups('@+!+!'), [1,2]);
        });

        test("range.result.group", () {
            expect(rangeGroups('@'), [1]);
            expect(rangeGroups('@+!'), [1,2]);
            expect(rangeGroups('@+!+!'), [1,2,2]);
        });

        test("ranges change but cache stays", () {
            var c = new TestCell("8,400", "! * 4200", 2);
            c.focused();
            c.calculate(getColumnReturns(['2']));
            expect(c.resolver.nextGroup, 2);
            expect(c.resolver.results['!'].group, 1);
            c.text = '!*4200+@';
            c.calculate(getColumnReturns(['2']));
            expect(c.resolver.nextGroup, 3);
            expect(c.resolver.results['!'].group, 1);
            expect(c.resolver.results['@'].group, 2);
        });

    });

    group("RangeResult.start/end", () {

        test("top-down, no range", () {
            expect(index('@', [1, 2, 4]), [0, 0]);
            expect(index('@1', [1, 2, 4]), [0, 0]);
            expect(index('@3', [1, 2, 4]), [2, 2]);
        });

        test("top-down, with range", () {
            expect(index('@:3', [1, 2, 4]), [0, 2]);
            expect(index('@:1', [1, 2, 4]), [0, 0]);
            expect(index('@1:', [1, 2, 4]), [0, 2]);
            expect(index('@3:', [1, 2, 4]), [2, 2]);
            expect(index('@2:', [1, 2, 4]), [1, 2]);
        });

        test("bottom-up, no range", () {
            expect(index('!', [1, 2, 4]), [2, 2]);
            expect(index('!1', [1, 2, 4]), [2, 2]);
            expect(index('!3', [1, 2, 4]), [0, 0]);
        });

        test("bottom-up, with range", () {
            expect(index('!:3', [1, 2, 4]), [0, 2]);
            expect(index('!:1', [1, 2, 4]), [2, 2]);
            expect(index('!1:', [1, 2, 4]), [0, 2]);
            expect(index('!3:', [1, 2, 4]), [0, 0]);
            expect(index('!2:', [1, 2, 4]), [0, 1]);
        });

        test("equation stops, no matches", () {
            expect(index('!&:',  [1, 2, 4, 5]), [-1, -1]);
            expect(index('!:&',  [1, 2, 4, 5]), [-1, -1]);
            expect(index('!&:&', [1, 2, 4, 5]), [-1, -1]);
            expect(index('!3:&',   [1, 2, 4, 5], 2, 3), [-1, -1]);
            expect(index('@&:',  [1, 2, 4, 5]), [-1, -1]);
            expect(index('@:&',  [1, 2, 4, 5]), [-1, -1]);
            expect(index('@&:&', [1, 2, 4, 5]), [-1, -1]);
            expect(index('@3:&',   [1, 2, 4, 5], 0, 1), [-1, -1]);
        });

        test("equation stops, with matches", () {
            expect(index('!&',   [1, 2, 4, 5], 1, 3), [3, 3]);
            expect(index('!&:&', [1, 2, 4, 5], 1, 3), [3, 3]);
            expect(index('!2:&', [1, 2, 4, 5], 0), [0, 2]);
            expect(index('!&:3', [1, 2, 4, 5], 3), [1, 3]);
            expect(index('@&',   [1, 2, 4, 5], 1, 3), [1, 1]);
            expect(index('@&:&', [1, 2, 4, 5], 1, 3), [1, 1]);
            expect(index('@2:&', [1, 2, 4, 5], 2), [1, 2]);
            expect(index('@&:3', [1, 2, 4, 5], 1), [1, 2]);
        });

    });

    group("Cell attributes", () {

        test("isBlank", () {
            expect(cell('').isTextBlank, isTrue);
            expect(cell('0').isTextBlank, isTrue);
            expect(cell('-0.0').isTextBlank, isTrue);
            expect(cell('-0.1').isTextBlank, isFalse);
        });

        test("isNumber", () {
            expect(cell('').isTextNumber, isFalse);
            expect(cell('0').isTextNumber, isTrue);
            expect(cell('-0.0').isTextNumber, isTrue);
            expect(cell('-0.1').isTextNumber, isTrue);
        });

        test("isEquation", () {
            expect(cell('').isTextEquation, isFalse);
            expect(cell('0').isTextEquation, isFalse);
            expect(cell('1,0.0').isTextEquation, isFalse);
            expect(cell('-10').isTextEquation, isFalse);
            expect(cell('1+1').isTextEquation, isTrue);
            expect(cell('A').isTextEquation, isTrue);
            expect(cell('!:').isTextEquation, isTrue);
            expect(cell('!+!+!').isTextEquation, isTrue);
        });

    });

    group("Cell.calculate(): value", () {

        test("single number ranges", () {
            expect(cellTotal('!+!+!', [1,2]), 6);
            expect(cellTotal('!2+!2+!2', [1,2]), 3);
            expect(cellTotal('@+@+@', [1,2]), 3);
            expect(cellTotal('@2+@2+@2', [1,2]), 6);
        });

        test("ranges, bottom-up", () {
            expect(cellTotal('!2:4+!5:', [1,2,3,4,5,6]), 15);
            expect(cellTotal('!:3+!5:', [1,2,3,4,5,6]), 18);
            expect(cellTotal('!:2+!4', [1,2,3,4,5,6]), 14);
        });

        test("ranges, top-down", () {
            expect(cellTotal('@2:4+@5:', [1,2,3,4,5,6]), 20);
            expect(cellTotal('@:3+@5:', [1,2,3,4,5,6]), 17);
            expect(cellTotal('@:2+@4', [1,2,3,4,5,6]), 7);
        });

        test("ranges, mixed", () {
            expect(cellTotal('@:2+!:2', [1,2,3,4,5,6]), 14);
            expect(cellTotal('@:3+!:3', [1,2,3,4,5,6]), 21);
            expect(cellTotal('@:+!:', [1,2,3,4,5,6]), 42);
            expect(cellTotal('A! + B!', [6]), 12);
        });

        test("solve with negative numbers", () {
            expect(cellTotal("-16/(5-3)"), -8.0);
            expect(cellTotal("-1+!2:&", [4,1,2,3], 1), 2);
            expect(cellTotal(" -16.0 / (5-3) "), -8.0);
            expect(cellTotal(" 16.0 /  -1*(5-3) "), -32.0);
            expect(cellTotal(" 16.0 / (-1*(5-3)) "), -8.0);
            expect(cellTotal("  -16/(5 +-3)"), -8.0);
        });

    });

    group("Cell.calculate(): phases", () {

        expectCell(TestCell c, {text: "", canonical: "", local: "", resolved: "",
                                preview: "", decimal: null, isChanged: false,
                                canonicalToLocal: 0, localToCanonical: 0,
                                localToResolved: 0, eval: 0,
                                canonicalToLocalAccessed: null, localToCanonicalAccessed: null,
                                localToResolvedAccessed: null, evalAccessed: null}) {
            expect(c.isChanged, isChanged, reason: "isChanged");
            expect(c.text, text, reason: "text");
            expect(c.canonical, canonical, reason: "canonical");
            expect(c.local, local, reason: "local");
            expect(c.resolved, resolved, reason: "resolved");
            expect(c.preview, preview, reason: "preview");
            expect(c.value?.decimal, decimal, reason: "value.decimal");
            expect(c.canonicalToLocalCreated, canonicalToLocal);
            expect(c.localToCanonicalCreated, localToCanonical);
            expect(c.localToResolvedCreated, localToResolved);
            expect(c.evalCreated, eval);
            expect(c.canonicalToLocalAccessed, canonicalToLocalAccessed == null ? canonicalToLocal : canonicalToLocalAccessed);
            expect(c.localToCanonicalAccessed, localToCanonicalAccessed == null ? localToCanonical : localToCanonicalAccessed);
            expect(c.localToResolvedAccessed, localToResolvedAccessed == null ? localToResolved : localToResolvedAccessed);
            expect(c.evalAccessed, evalAccessed == null ? eval : evalAccessed);
        }

        /* Test interaction pattern should roughly be:

            var c = new TestCell();
            c.focused();
            c.calculate((i)=>[]); // focus always triggers calculate

            // ... change something ...  c.text = "99";
            expectCell(c, ..., isChanged: true);
            c.calculate((i)=>[]); // input always triggers calculate
            expectCell(c, ...);
            // ... repeat above as necessary ...

            c.blurred();
            expectCell(c, ...);  // check cleanup is correct

            c.focused();
            c.calculate((i)=>[]); // focus always triggers calculate
            expectCell(c, ...); // check modified state loaded correctly

         */

        test("blank", () {
            var c = new TestCell();
            c.focused();
            c.calculate((i)=>[]);
            expectCell(c);
            c.blurred();
            expectCell(c);
            c.focused();
            c.calculate((i)=>[]);
            expectCell(c);
        });

        test("blank -> number -> blank", () {
            var c = new TestCell();
            c.focused();
            c.calculate((i) => []);

            c.text = "4,200";
            expectCell(c,
                text: "4,200",
                isChanged: true);

            c.calculate((i) => []);
            expectCell(c,
                text: "4,200",
                canonical: "4200",
                decimal: 4200);

            c.blurred();
            expectCell(c,
                text: "4,200",
                canonical: "4200",
                decimal: 4200);

            c.focused();
            c.calculate((i)=>[]);
            expectCell(c,
                text: "4,200",
                canonical: "4200",
                decimal: 4200);

            c.text = "";
            expectCell(c,
                text: "",
                canonical: "4200",
                decimal: 4200,
                isChanged: true);

            c.calculate((i) => []);
            expectCell(c);

            c.blurred();
            expectCell(c);

            c.focused();
            c.calculate((i)=>[]);
            expectCell(c);

        });

        test("blank -> equation (price col) -> blank", () {

            var c = new TestCell();
            c.column = 1;
            c.focused();
            c.calculate(getColumnReturns(['2']));

            c.text = "!*4,200";
            expectCell(c,
                text: "!*4,200",
                isChanged: true);

            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "!*4,200",
                canonical: "! * 4200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                preview: "2 * 4,200 = 8,400.00",
                decimal: 8400, eval: 1);

            c.blurred();
            expectCell(c,
                text: "8,400.00",
                canonical: "! * 4200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                preview: "2 * 4,200 = 8,400.00",
                decimal: 8400, eval: 1);

            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "! * 4,200",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                localToResolvedAccessed: 2,
                preview: "2 * 4,200 = 8,400.00",
                decimal: 8400, eval: 1);

            c.text = "";
            expectCell(c,
                text: "",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                localToResolvedAccessed: 2,
                preview: "2 * 4,200 = 8,400.00",
                decimal: 8400, eval: 1,
                isChanged: true);

            c.calculate(getColumnReturns(['2']));
            expectCell(c, canonicalToLocal: 1, localToCanonical: 1, localToResolved: 1, localToResolvedAccessed: 2, eval: 1);

            c.blurred();
            expectCell(c, canonicalToLocal: 1, localToCanonical: 1, localToResolved: 1, localToResolvedAccessed: 2, eval: 1);

            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c, canonicalToLocal: 1, localToCanonical: 1, localToResolved: 1, localToResolvedAccessed: 2, eval: 1);

        });

        test("blank -> equation (qty col) -> blank", () {

            var c = new TestCell();
            c.column = 0;
            c.focused();
            c.calculate(getColumnReturns(['2']));

            c.text = "!*4,200";
            expectCell(c,
                text: "!*4,200",
                isChanged: true);

            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "!*4,200",
                canonical: "! * 4200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 1);

            c.blurred();
            expectCell(c,
                text: "8,400",
                canonical: "! * 4200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 1);

            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "! * 4,200",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                localToResolvedAccessed: 2,
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 1);

            c.text = "";
            expectCell(c,
                text: "",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                localToResolvedAccessed: 2,
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 1,
                isChanged: true);

            c.calculate(getColumnReturns(['2']));
            expectCell(c, canonicalToLocal: 1, localToCanonical: 1, localToResolved: 1, localToResolvedAccessed: 2, eval: 1);

            c.blurred();
            expectCell(c, canonicalToLocal: 1, localToCanonical: 1, localToResolved: 1, localToResolvedAccessed: 2, eval: 1);

            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c, canonicalToLocal: 1, localToCanonical: 1, localToResolved: 1, localToResolvedAccessed: 2, eval: 1);

        });

        test("number -> equation", () {

            var c = new TestCell("4,200", "4200");
            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c, text: "4,200", canonical: "4200", decimal: 4200);

            c.text = "!*4,200";
            expectCell(c,
                text: "!*4,200",
                canonical: "4200",
                decimal: 4200,
                isChanged: true);

            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "!*4,200",
                canonical: "! * 4200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 1);

            c.blurred();
            expectCell(c,
                text: "8,400",
                canonical: "! * 4200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 1);

            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "! * 4,200",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToCanonical: 1,
                resolved: "2 * 4,200",
                localToResolved: 1,
                localToResolvedAccessed: 2,
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 1);

        });

        test("equation -> number -> equation", () {

            var c = new TestCell("8,400", "! * 4200");
            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "! * 4,200",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToResolved: 1,
                resolved: "2 * 4,200",
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 0);

            c.text = "4200";
            expectCell(c,
                text: "4200",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToResolved: 1,
                resolved: "2 * 4,200",
                preview: "2 * 4,200 = 8,400",
                decimal: 8400, eval: 0,
                isChanged: true);

            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "4200",
                canonical: "4200",
                canonicalToLocal: 1, localToResolved: 1, eval: 0,
                decimal: 4200);

            c.blurred();
            expectCell(c,
                text: "4,200",
                canonical: "4200",
                canonicalToLocal: 1, localToResolved: 1, eval: 0,
                decimal: 4200);

            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "4,200",
                canonical: "4200",
                canonicalToLocal: 1, localToResolved: 1, eval: 0,
                decimal: 4200);

            c.text = "!*4,200";
            expectCell(c,
                text: "!*4,200",
                canonical: "4200",
                canonicalToLocal: 1, localToResolved: 1, eval: 0,
                decimal: 4200,
                isChanged: true);

            c.calculate(getColumnReturns(['2']));
            // ran three parsers: localToCanonical (1st time), localToResolved (2nd time), eval (1st time)
            expectCell(c,
                text: "!*4,200",
                canonical: "! * 4200",
                localToCanonical: 1, canonicalToLocal: 1, localToResolved: 1, eval: 1,
                localToResolvedAccessed: 2,
                resolved: "2 * 4,200",
                preview: "2 * 4,200 = 8,400",
                decimal: 8400);

            c.blurred();
            // no parsers accessed, just the usual value->text swap
            expectCell(c,
                text: "8,400",
                canonical: "! * 4200",
                localToCanonical: 1, canonicalToLocal: 1, localToResolved: 1, eval: 1,
                localToResolvedAccessed: 2,
                resolved: "2 * 4,200",
                preview: "2 * 4,200 = 8,400",
                decimal: 8400);

            c.focused();
            c.calculate(getColumnReturns(['2']));
            // had to run canonicalToLocal to get the local version of equation
            expectCell(c,
                text: "! * 4,200",
                canonical: "! * 4200",
                local: "! * 4,200",
                localToCanonical: 1, canonicalToLocal: 1, localToResolved: 1, eval: 1,
                canonicalToLocalAccessed: 2, localToResolvedAccessed: 3,
                resolved: "2 * 4,200",
                preview: "2 * 4,200 = 8,400",
                decimal: 8400);

            c.blurred();
            c.focused();
            c.calculate(getColumnReturns(['2']));
            // nothing should have changed
            expectCell(c,
                text: "! * 4,200",
                canonical: "! * 4200",
                local: "! * 4,200",
                localToCanonical: 1, canonicalToLocal: 1, localToResolved: 1, eval: 1,
                canonicalToLocalAccessed: 2, localToResolvedAccessed: 3,
                resolved: "2 * 4,200",
                preview: "2 * 4,200 = 8,400",
                decimal: 8400);

        });

        test("equation -> equation", () {

            var c = new TestCell("8,400", "! * 4200", 2);
            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "! * 4,200",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToResolved: 1,
                resolved: "2 * 4,200",
                preview: "2 * 4,200 = 8,400.00",
                decimal: 8400, eval: 0);

            c.text = "!*4,200+@";
            expectCell(c,
                text: "!*4,200+@",
                canonical: "! * 4200",
                canonicalToLocal: 1,
                local: "! * 4,200",
                localToResolved: 1,
                resolved: "2 * 4,200",
                preview: "2 * 4,200 = 8,400.00",
                decimal: 8400, eval: 0,
                isChanged: true);

            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "!*4,200+@",
                canonical: "(! * 4200) + @",
                localToCanonical: 1, canonicalToLocal: 1, localToResolved: 1, eval: 1,
                canonicalToLocalAccessed: 1, localToResolvedAccessed: 2,
                resolved: "(2 * 4,200) + 2",
                preview: "(2 * 4,200) + 2 = 8,402.00",
                decimal: 8402);

            c.blurred();
            expectCell(c,
                text: "8,402.00",
                canonical: "(! * 4200) + @",
                localToCanonical: 1, canonicalToLocal: 1, localToResolved: 1, eval: 1,
                canonicalToLocalAccessed: 1, localToResolvedAccessed: 2,
                resolved: "(2 * 4,200) + 2",
                preview: "(2 * 4,200) + 2 = 8,402.00",
                decimal: 8402);

            c.focused();
            c.calculate(getColumnReturns(['2']));
            expectCell(c,
                text: "(! * 4,200) + @",
                canonical: "(! * 4200) + @",
                local: "(! * 4,200) + @",
                localToCanonical: 1, canonicalToLocal: 1, localToResolved: 1, eval: 1,
                canonicalToLocalAccessed: 2, localToResolvedAccessed: 3,
                resolved: "(2 * 4,200) + 2",
                preview: "(2 * 4,200) + 2 = 8,402.00",
                decimal: 8402);

        });

        test("equation -> [calculate] -> [calculate:dependencyChanged]", () {

            var c = new TestCell("4,200", "! * 4200");
            expectCell(c, text: "4,200", canonical: "! * 4200");

            c.calculate(getColumnReturns(['2']));
            // decimal set but not calculated because not told that dependecyChanged
            expectCell(c, text: "4,200", canonical: "! * 4200", decimal: 4200);

            c.calculate(getColumnReturns(['2']), true);
            // same thing as above but this time we are told dependencyChanged
            expectCell(c, text: "8,400", canonical: "! * 4200", decimal: 8400, eval: 1);

        });

        test("number -> [calculate] -> [calculate:dependencyChanged]", () {

            var c = new TestCell("4,200");
            expectCell(c, text: "4,200");

            c.calculate(getColumnReturns(['2']));
            expectCell(c, text: "4,200", decimal: 4200);

            c.calculate(getColumnReturns(['2']), true);
            // numbers are not evaluated
            expectCell(c, text: "4,200", decimal: 4200);

        });

        test("empty cell dynamically set and then focused", () {
            var c = new TestCell("", "", 2);
            expectCell(c);
            c.setCalculated(new Decimal(93, 3));
            expectCell(c, text: "93.00", preview: "93.00", decimal: 93);
            c.focused();
            c.calculate((i)=>[]);
            expectCell(c, text: "", preview: "93.00", decimal: 93);
        });

        test("focused cell doesn't get reset during calculation", () {
            var c = new TestCell("93", "", 2);
            expectCell(c, text: "93");
            c.focused();
            expectCell(c, text: "", preview: "93.00", decimal: 93);
            c.calculate((i)=>[]);
            expectCell(c, text: "", preview: "93.00", decimal: 93);
            c.setCalculated(new Decimal(55, 3));
            expectCell(c, text: "", preview: "55.00", decimal: 55);
            c.blurred();
            expectCell(c, text: "55.00", preview: "55.00", decimal: 55);
        });

    });
}