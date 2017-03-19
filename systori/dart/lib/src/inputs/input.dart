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


class StyledInput extends TextInput {
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
