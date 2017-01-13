import 'dart:html';
import 'package:quiver/iterables.dart';
import 'package:systori/inputs.dart';


class Keyboard {

    int get caretOffset {
        var sel = window.getSelection();
        var offsetRange = new Range();
        offsetRange.selectNodeContents(document.activeElement);
        var range = sel.getRangeAt(0);
        offsetRange.setEnd(range.endContainer, range.endOffset);
        return offsetRange.toString().length;
    }

    set caretOffset(int offset) {
        var sel = window.getSelection();
        Node node;
        for (node in traverse(document.activeElement)) {
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

    caretToEnd() {
        var sel = window.getSelection();
        sel.removeAllRanges();
        var range = new Range();
        range.selectNodeContents(document.activeElement);
        range.collapse();
        sel.addRange(range);
    }

    sendEnter([int times = 1]) => sendKey(KeyCode.ENTER, times);
    sendUp([int times = 1]) => sendKey(KeyCode.UP, times);
    sendDown([int times = 1]) => sendKey(KeyCode.DOWN, times);
    sendKey(int keyCode, [int times = 1]) {
        Input input = document.activeElement;
        range(times).forEach((i) {
            input.dispatchKeyDownEvent(new KeyEvent('keydown', keyCode: keyCode));
            input.dispatchKeyUpEvent(new KeyEvent('keyup', keyCode: keyCode));
        });
    }

    sendText(String text) {
        Input input = document.activeElement;
        var sel = window.getSelection();
        var range = sel.getRangeAt(0);
        range.deleteContents();
        text.codeUnits.forEach((int key) {
            input.dispatchKeyDownEvent(new KeyEvent('keydown', charCode: key));
            var character = new Text(new String.fromCharCode(key));
            range.insertNode(character);
            range.setStartAfter(character);
            input.dispatchInputEvent();
            input.dispatchKeyUpEvent(new KeyEvent('keyup', charCode: key));
        });
        sel.removeAllRanges();
        sel.addRange(range);
    }

    setText(String text) {
        selectAll();
        sendText(text);
    }

    selectAll() {
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(new Range()..selectNodeContents(document.activeElement));
    }

}

Iterable<Node> traverse(Node root) sync* {
    for (var node in root.childNodes) {
        yield* traverse(node);
        yield node;
    }
}
