@TestOn('browser')
import 'dart:html';
import 'package:quiver/iterables.dart';
import 'package:test/test.dart';
import 'package:systori/orderable.dart';

class OrderableElement extends HtmlElement with Orderable {
    OrderableElement.created(): super.created();
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

printVisibleNodeNames() {
    /* Useful for checking that content shell has the elements on
       screen.
     */
    range(500).forEach((y) {
        var el = document.elementFromPoint(20, y);
        if (el!=null) {
            print("$y ${el.nodeName}: ${el.text.length >= 20 ? el.text.substring(0, 20)+'...' : el.text}");
        }
    });
}

void main() {
    registerOrderableContainerElement();
    document.registerElement('orderable-item', OrderableElement);

    group("Orderable", () {

        test("move item in first container, before scroll", () {
            /*  this test is tricky in content-shell because the screen
                appears to only be 150 high x 284 wide... so the list
                is not even visible on the screen, to still somewhat
                emulate offsetting we at least scroll to the first P tag
             */
            var container = querySelector('#first-container');
            var first = container.children.first;
            querySelector('p').scrollIntoView(ScrollAlignment.TOP);
            expect(container.children.indexOf(first), 0);
            //printVisibleNodeNames();
            mouseDownAt(10, 30);
            mouseMoveTo(10, 70);
            mouseUp();
            expect(container.children.indexOf(first), 2);
        });

        test("move item in second container, after scroll", () {
            var container = querySelector('#second-container');
            var first = container.children.first;
            container.scrollIntoView(ScrollAlignment.TOP);
            expect(container.children.indexOf(first), 0);
            var offset = container.offsetTop - window.scrollY;
            //printVisibleNodeNames();
            mouseDownAt(10, 10+offset);
            mouseMoveTo(10, 50+offset);
            mouseUp();
            expect(container.children.indexOf(first), 2);
        });

    });
}
