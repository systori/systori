import 'dart:html';
import 'package:test/test.dart';
import 'package:systori/orderable_container.dart';

class AOrderable extends HtmlElement with Orderable {
    AOrderable.created(): super.created();
}

mouseUp() => document.dispatchEvent(new MouseEvent('mouseup'));
mouseDownAt(int x, int y) {
    var element = document.elementFromPoint(x, y);
    var event = new MouseEvent('mousedown',
        screenX: x, screenY: y,
        clientX: x, clientY: y,
    );
    element.dispatchEvent(event);
}

mouseMoveTo(int x, int y) {
    var event = new MouseEvent('mousemove',
        screenX: x, screenY: y,
        clientX: x, clientY: y,
    );
    document.dispatchEvent(event);
}

void main() {
    registerOrderableContainer();
    document.registerElement('orderable-item', AOrderable);

    group("Orderable", () {

        test("move item in first container, before scroll", () {
            var container = querySelector('#first-container');
            var first = container.children.first;
            expect(container.children.indexOf(first), equals(0));
            container.scrollIntoView();
            var offset = container.offsetTop - window.scrollY;
            mouseDownAt(10, 10+offset);
            mouseMoveTo(10, 50+offset);
            mouseUp();
            expect(container.children.indexOf(first), equals(2));
        });

        test("move item in second container, after scroll", () {
            var container = querySelector('#second-container');
            var first = container.children.first;
            expect(container.children.indexOf(first), equals(0));
            container.scrollIntoView();
            var offset = container.offsetTop - window.scrollY;
            mouseDownAt(10, 10+offset);
            mouseMoveTo(10, 50+offset);
            mouseUp();
            expect(container.children.indexOf(first), equals(2));
        });

    });
}
