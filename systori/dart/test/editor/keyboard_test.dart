@TestOn("browser")
import 'dart:html';
import 'package:test/test.dart';
import 'package:mockito/mockito.dart';
import 'package:systori/editor.dart';

class MockNavigationReceiver extends Mock implements NavigationReceiver {}

main() {

    group("KeyboardNavigation", () {

        KeyboardNavigator nav;
        NavigationReceiver receiver;

        setUp(() {
            receiver = new MockNavigationReceiver();
            nav = new KeyboardNavigator(receiver);
        });

        test("onUp()", () {
            nav.handleKey(new KeyEvent('', keyCode: KeyCode.UP));
            verify(receiver.onUp());
        });

        test("onNewSibling()", () {
            nav.handleKey(new KeyEvent('', keyCode: KeyCode.ENTER));
            verify(receiver.onNewSibling());
        });

    });
}