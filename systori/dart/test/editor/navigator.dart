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

    reset() {
        Job job = querySelector('sys-job');
        job.name.focus();
    }

    sendKey(int keyCode, [int times = 1]) {
        Input input = document.activeElement;
        range(times).forEach((i) {
            input.controller.add(new KeyEvent('keydown', keyCode: keyCode));
        });
    }

    sendEnter([int times = 1]) => sendKey(KeyCode.ENTER, times);
    sendUp([int times = 1]) => sendKey(KeyCode.UP, times);
    sendDown([int times = 1]) => sendKey(KeyCode.DOWN, times);
    sendText(String text) {
        Input input = document.activeElement;
        text.codeUnits.forEach((int key) {
            input.appendText(new String.fromCharCode(key));
            input.controller.add(new KeyEvent('keydown', charCode: key));
        });
    }

}

