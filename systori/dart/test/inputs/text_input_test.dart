@TestOn("browser")
import 'dart:html';
import 'package:test/test.dart';
import 'package:systori/inputs.dart';
import '../keyboard.dart';


main() {

    document.registerElement('styled-input', StyledInput);

    Keyboard keyboard = new Keyboard();
    StyledInput input = querySelector('styled-input');

    group("Clean HTML", () {

        test("breaks", () {
            expect(cleanHtml('hi <div>foo</div> bar'), equals('hi <br />foo<br /> bar'));
            expect(cleanHtml('hi <p>foo</p> bar'), equals('hi <br />foo<br /> bar'));
            expect(cleanHtml('hi <span style="display: block;">foo</span> bar'), equals('hi <br />foo<br /> bar'));
        });

        test("bold", () {
            expect(cleanHtml('hi <b>foo</b>!'), equals('hi <b>foo</b>!'));
            expect(cleanHtml('hi <span style="font-weight: bold;">foo</span>!'), equals('hi <b>foo</b>!'));
            expect(cleanHtml('hi <span style="font-weight: 400;">foo</span>!'), equals('hi foo!'));
            expect(cleanHtml('hi <span style="font-weight: 500;">foo</span>!'), equals('hi foo!'));
            expect(cleanHtml('hi <span style="font-weight: 600;">foo</span>!'), equals('hi <b>foo</b>!'));
            expect(cleanHtml('hi <span style="font-weight: 700;">foo</span>!'), equals('hi <b>foo</b>!'));
            expect(cleanHtml('hi <span style="font-weight: 800;">foo</span>!'), equals('hi <b>foo</b>!'));
            expect(cleanHtml('hi <span style="font-weight: 900;">foo</span>!'), equals('hi <b>foo</b>!'));
        });

        test("talic", () {
            expect(cleanHtml('hi <i>foo</i>!'), equals('hi <i>foo</i>!'));
            expect(cleanHtml('hi <span style="font-style: italic;">foo</span>!'), equals('hi <i>foo</i>!'));
        });

        test("underline", () {
            expect(cleanHtml('hi <u>foo</u>!'), equals('hi <u>foo</u>!'));
            expect(cleanHtml('hi <span style="text-decoration: underline;">foo</span>!'), equals('hi <u>foo</u>!'));
        });

        test("all styles", () {
            expect(cleanHtml('hi <i><b><u>foo</u></b></i>!'), equals('hi <i><b><u>foo</u></b></i>!'));
            expect(cleanHtml('hi <span style="font-weight: bold; font-style: italic; text-decoration: underline;">foo</span>!'),
                    equals('hi <b><i><u>foo</u></i></b>!'));
        });

    });

    group("Paste", () {

        setUp(() {
            input.setInnerHtml('foo <b>bar</b> baz');
            input.focus();
        });

        test("inserts cleaned html at caret location", () {
            keyboard.caretOffset = 8;
            input.handlePaste("<div><i><video></video>fuzz</i></div>");
            expect(input.innerHtml, equals("foo <b>bar</b> <br><i>fuzz</i><br>baz"));
        });

    });

}
