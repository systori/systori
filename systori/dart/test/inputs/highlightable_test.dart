@TestOn("browser")
import 'dart:html';
import 'package:test/test.dart';
import 'package:systori/inputs.dart';


class HighlightableInput extends HtmlElement with HighlightableInputMixin {
    HighlightableInput.created(): super.created() {
        contentEditable = "true";
    }
}


String setCaretAt(Node node) {
    var sel = window.getSelection();
    var range = new Range();
    range.selectNodeContents(node);
    var result = range.toString();
    range.collapse(true);
    sel.removeAllRanges();
    sel.addRange(range);
    return result;
}

String getAtCaret() {
    var sel = window.getSelection();
    var range = sel.getRangeAt(0);
    range.selectNodeContents(range.startContainer);
    return range.toString();
}


main() {

    document.registerElement('highlight-input', HighlightableInput);

    group("HighlightableInput", () {

        test("highlight()", () {
            HighlightableInput input = querySelector('highlight-input');

            expect(setCaretAt(input.childNodes.last), equals('baz'));

            expect(input.innerHtml, equals("foo<span>bar</span>baz"));
            expect(getAtCaret(), equals('baz'));

            input.highlight([
                new Highlight(1,2,null),
                new Highlight(5,8,null)
            ]);

            expect(input.innerHtml, equals("f<span>o</span>oba<span>rba</span>z"));
            expect(getAtCaret(), equals('rba'));

        });

    });
}
