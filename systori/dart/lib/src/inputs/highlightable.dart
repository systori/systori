import 'dart:html';


Iterable<Node> traverse(Node root) sync* {
    for (var node in root.childNodes) {
        yield* traverse(node);
        yield node;
    }
}


class Highlight {
    int start;
    int end;
    String color;
    Highlight(this.start, this.end, this.color);
}


abstract class HighlightableInputMixin implements HtmlElement {

    highlight(Iterable<Highlight> highlights) {

        var buffer = new StringBuffer();

        int lastEnd = 0;
        for (var highlight in highlights) {
            buffer.write(text.substring(lastEnd, highlight.start));
            buffer.write('<span');
            if (highlight.color!=null)
                buffer.write(' style="background: rgba(${highlight.color},0.2);"');
            buffer.write('>');
            buffer.write(text.substring(highlight.start, highlight.end));
            buffer.write('</span>');
            lastEnd = highlight.end;
        }
        buffer.write(text.substring(lastEnd));

        var caretOffset = getCaretOffset();
        setInnerHtml(
            buffer.toString(),
            treeSanitizer: NodeTreeSanitizer.trusted
            //validator: new NodeValidatorBuilder.common()
            //    ..allowElement('span', attributes: ['style'])
        );
        setCaret(caretOffset);
    }

    int getCaretOffset() {
        var sel = window.getSelection();
        var offsetRange = new Range();
        offsetRange.selectNodeContents(this);
        var range = sel.getRangeAt(0);
        offsetRange.setEnd(range.endContainer, range.endOffset);
        return offsetRange.toString().length;
    }

    setCaret(int offset) {
        var sel = window.getSelection();
        Node node;
        for (node in traverse(this)) {
            if (node.nodeType == Node.TEXT_NODE) {
                var length = (node as Text).length;
                if (offset <= length)
                    break;
                offset -= length;
            }
        }
        if (node != null) {
            var range = new Range();
            range.setStart(node, offset);
            sel.removeAllRanges();
            sel.addRange(range);
        }
    }
}

