import 'dart:html';


abstract class KeyboardReceiver implements Element {
    onUp() {}
    onNewSibling() {}
}


class KeyboardManager {

    NavigationReceiver receiver;

    KeyboardNavigator(this.receiver);

    handleKey(KeyboardEvent event) {
        switch (event.keyCode) {
            case KeyCode.UP:    receiver.onUp(); break;
            case KeyCode.ENTER: receiver.onNewSibling(); break;
        }
    }
}