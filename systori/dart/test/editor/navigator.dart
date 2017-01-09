import 'dart:html';
import 'package:quiver/iterables.dart';
import 'package:systori/editor.dart';


class KeyboardNavigator {

    Model get activeModel {
        var e = document.activeElement;
        while (e != null) {
            if (e is Model) return e;
            e = e.parent;
        }
        return null;
    }

    sendKey(int keyCode, [int times = 1]) {
        Input input = document.activeElement;
        range(times).forEach((i) {
            input.dispatchKeyDownHandlers(new KeyEvent('keydown', keyCode: keyCode));
        });
        range(times).forEach((i) {
            input.dispatchKeyUpHandlers(new KeyEvent('keyup', keyCode: keyCode));
        });
    }

    sendEnter([int times = 1]) => sendKey(KeyCode.ENTER, times);
    sendUp([int times = 1]) => sendKey(KeyCode.UP, times);
    sendDown([int times = 1]) => sendKey(KeyCode.DOWN, times);
    sendText(String text) {
        Input input = document.activeElement;
        text.codeUnits.forEach((int key) {
            input.dispatchKeyDownHandlers(new KeyEvent('keydown', charCode: key));
            input.appendText(new String.fromCharCode(key));
            input.dispatchKeyUpHandlers(new KeyEvent('keyup', charCode: key));
        });
    }

}

