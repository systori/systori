import 'dart:html';


abstract class KeyboardHandler {
    bool onKeyDownEvent(KeyEvent e, Input input) => false;
    bool onKeyUpEvent(KeyEvent e, Input input) => false;
    onFocusEvent(Input input) {}
    onBlurEvent(Input input) {}
    onInputEvent(Input input) {}
    bindAll(Iterable<Input> inputs) =>
        inputs.forEach((Input input) =>
            input.addHandler(this));
}


class Input extends HtmlElement {

    Map<String,dynamic> get values => {className: text};

    List<KeyboardHandler> _handlers = [];

    Input.created(): super.created() {
        onFocus.listen((Event e) =>
            _handlers.forEach((h) => h.onFocusEvent(this))
        );
        onKeyDown.listen((KeyboardEvent e) =>
            dispatchKeyDownEvent(new KeyEvent.wrap(e))
        );
        onInput.listen((Event e) =>
            dispatchInputEvent()
        );
        onKeyUp.listen((KeyboardEvent e) =>
            dispatchKeyUpEvent(new KeyEvent.wrap(e))
        );
        onBlur.listen((Event e) =>
            _handlers.forEach((h) => h.onBlurEvent(this))
        );
    }

    addHandler(KeyboardHandler handler) {
        _handlers.add(handler);
    }

    dispatchKeyDownEvent(KeyEvent e) =>
        _handlers.any((h) => h.onKeyDownEvent(e, this));

    dispatchInputEvent() =>
        _handlers.forEach((h) => h.onInputEvent(this));

    dispatchKeyUpEvent(KeyEvent e) =>
        _handlers.any((h) => h.onKeyUpEvent(e, this));

}


class StyledInput extends Input {
    Map<String,dynamic> get values => {
        className: innerHtml
            .replaceAll('<div>', '<br />')
            .replaceAll('</div>', '')
            // can't support formatting yet
            .replaceAll(new RegExp(r'<\/?i>'), '')
            .replaceAll(new RegExp(r'<\/?b>'), '')
            .replaceAll(new RegExp(r'<\/?span.*?>'), '')
            .replaceAll('<br>', '<br />')
    };
    StyledInput.created(): super.created();
}
