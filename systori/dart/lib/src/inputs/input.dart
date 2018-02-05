import 'dart:html';

abstract class EventHandler {
    onInputEvent(Input input) {}
}


abstract class KeyboardHandler implements EventHandler {
    /*
        onKeyDownEvent() and onKeyUpEvent()
        returns false: continue calling subsequent event handlers
        returns true: event was handled, stop propagating
     */
    bool onKeyDownEvent(KeyEvent e, TextInput input) => false;
    bool onKeyPressEvent(KeyEvent e, TextInput input) => false;
    bool onKeyUpEvent(KeyEvent e, TextInput input) => false;
    onFocusEvent(TextInput input) {}
    onBlurEvent(TextInput input) {}
    onInputEvent(Input input) {}
    bindAll(Iterable<TextInput> inputs) =>
        inputs.forEach((TextInput input) =>
            input.addKeyHandler(this));
}


class Input extends HtmlElement {

    String get name => classes.first;
    Map<String,dynamic> get values => {name: text};
    List<EventHandler> _eventHandlers = [];

    Input.created(): super.created();

    addHandler(EventHandler handler) =>
        _eventHandlers.add(handler);

    dispatchInputEvent() =>
        _eventHandlers.forEach((h) => h.onInputEvent(this));
}


class TextInput extends Input {

    List<KeyboardHandler> _keyHandlers = [];

    TextInput.created(): super.created() {
        onFocus.listen((Event e) =>
            _keyHandlers.forEach((h) => h.onFocusEvent(this))
        );
        onKeyDown.listen((KeyboardEvent e) =>
            dispatchKeyDownEvent(new KeyEvent.wrap(e))
        );
        onKeyPress.listen((KeyboardEvent e) =>
            dispatchKeyPressEvent(new KeyEvent.wrap(e))
        );
        onKeyUp.listen((KeyboardEvent e) =>
            dispatchKeyUpEvent(new KeyEvent.wrap(e))
        );
        onInput.listen((Event e) =>
            dispatchInputEvent()
        );
        onBlur.listen((Event e) =>
            _keyHandlers.forEach((h) => h.onBlurEvent(this))
        );
    }

    addKeyHandler(KeyboardHandler handler) {
        _eventHandlers.add(handler);
        _keyHandlers.add(handler);
    }

    dispatchKeyDownEvent(KeyEvent e) =>
        _keyHandlers.any((h) => h.onKeyDownEvent(e, this));

    dispatchKeyPressEvent(KeyEvent e) =>
        _keyHandlers.any((h) => h.onKeyPressEvent(e, this));

    dispatchKeyUpEvent(KeyEvent e) =>
        _keyHandlers.any((h) => h.onKeyUpEvent(e, this));

}


Iterable<String> cleanNode(Node parent, [canBreak = true]) sync* {
    if (parent.nodeType == Node.TEXT_NODE) {
        yield parent.text;

    } else if (parent.nodeType == Node.ELEMENT_NODE) {
        Element element = parent;

        if (element.tagName == "BR") {
            if (canBreak) yield "<br />";
            return;
        }

        var block = false;
        if (['DIV', 'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6'].contains(element.tagName) ||
                element.style.display == "block") {
            block = true;
        }

        if (canBreak && block) yield "<br />";

        var tags = [];
        if (['B', 'I', 'U'].contains(element.tagName)) {

            tags = [element.tagName.toLowerCase()];
            yield "<${tags[0]}>";

        } else {

            if (['bold', '600', '700', '800', '900'].contains(element.style.fontWeight)) {
                yield "<b>"; tags.add('b');
            }

            if (element.style.fontStyle == 'italic') {
                yield "<i>"; tags.add('i');
            }

            if (element.style.textDecorationLine == 'underline') {
                yield "<u>"; tags.add('u');
            }

        }

        for (var node in parent.childNodes) {
            yield* cleanNode(node, tags.isEmpty && canBreak);
        }

        for (var tag in tags.reversed) {
            yield "</$tag>";
        }

        if (canBreak && block) yield "<br />";
    }
}


String cleanHtml(String html) {
    var span = new SpanElement();
    span.setInnerHtml(html, treeSanitizer: NodeTreeSanitizer.trusted);
    return cleanNode(span).join();
}


class StyledInput extends TextInput {

    Map<String,dynamic> get values => {
        className: cleanNode(this).join()
    };

    StyledInput.created(): super.created() {
        onPaste.listen((ClipboardEvent event) {
            event.preventDefault();
            event.clipboardData.types.contains('text/html') ?
                handlePaste(event.clipboardData.getData('text/html')) :
                handlePaste('', event.clipboardData.getData('text/plain'));
        });
    }

    handlePaste(String html, [String plain=""]) {
        var sel = window.getSelection();
        var range = sel.getRangeAt(0);
        range.deleteContents();
        if (html.isNotEmpty) {
            var frag = document.createDocumentFragment();
            frag.setInnerHtml(cleanHtml(html), treeSanitizer: NodeTreeSanitizer.trusted);
            range.insertNode(frag);
        } else {
            range.insertNode(new Text(plain));
        }
    }
}


class Toggle extends Input {

    bool get value => classes.contains('True');
    Map<String,dynamic> get values => {name: value};

    Toggle.created(): super.created() {
        onClick.listen((MouseEvent e) {
            value ? toggleOff() : toggleOn();
            dispatchInputEvent();
        });
    }

    toggleOff() {
        classes.remove('True');
        classes.add('False');
    }

    toggleOn() {
        classes.remove('False');
        classes.add('True');
    }

}
