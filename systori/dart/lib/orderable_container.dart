import 'dart:html';
import 'dart:async';


abstract class Orderable implements Element {

    isHit(int y) =>
        this.offset.top < y && y < this.offset.bottom;

    isHandle(Element handle) =>
        handle.classes.contains('${tagName.toLowerCase()}-handle');

}


abstract class OrderableContainer implements Element {

    StreamSubscription<MouseEvent> mouseDownSubscription;

    attached() => mouseDownSubscription = onMouseDown.listen(maybeStartDragging);

    detached() => mouseDownSubscription.cancel();

    Orderable findOrderable(Element child) {
        while (child != null) {
            if (child is Orderable) return child;
            if (child == this) return null;
            child = child.parent;
        }
        return null;
    }

    maybeStartDragging(MouseEvent e) {

        var orderable = findOrderable(e.target);

        if (orderable == null || !orderable.isHandle(e.target)) {
            return;
        }

        var rec = this.getBoundingClientRect();
        var parentTopPage = rec.top + window.scrollY;
        var parentBottomPage = rec.bottom + window.scrollY;
        var startMousePositionPage = e.page.y;
        var orderableTopRelative = orderable.offset.top;

        // add placeholder
        DivElement placeholder = document.createElement('div');
        placeholder.classes.add('${orderable.tagName.toLowerCase()}-placeholder');
        placeholder.style.height = "${orderable.offsetHeight}px";
        placeholder.style.width = "${orderable.offsetWidth}px";
        insertBefore(placeholder, orderable.nextElementSibling);

        // start dragging the orderable
        orderable.style.top = "${orderableTopRelative}px";
        orderable.style.width = "${orderable.offsetWidth}px";
        orderable.style.position = "absolute";
        orderable.style.zIndex = "1000";

        var previousMousePosition = startMousePositionPage;
        var movement = document.onMouseMove.listen((MouseEvent e) {
            if (parentTopPage > e.page.y || e.page.y > parentBottomPage) return;

            var moved = e.page.y - startMousePositionPage;
            orderable.style.top = "${orderableTopRelative+moved}px";

            var over, relativeMousePosition = e.page.y - parentTopPage;
            for (var child in this.children) {
                if (child != orderable && child is Orderable && child.isHit(relativeMousePosition)) {
                    over = child;
                    break;
                }
            }

            var delta = e.page.y - previousMousePosition;
            if (over != null) {
                if (delta > 0) {
                    insertBefore(placeholder, over.nextElementSibling);
                } else {
                    insertBefore(placeholder, over);
                }
            }

            previousMousePosition = e.page.y;
        });

        document.onMouseUp.first.then((MouseEvent e) {
            movement.cancel();
            insertBefore(orderable, placeholder);
            placeholder.remove();
            orderable.style.top = null;
            orderable.style.width = null;
            orderable.style.position = null;
            orderable.style.zIndex = null;
            onOrderingFinished(orderable);
        });
    }

    onOrderingFinished(Orderable orderable) {}
}


class OrderableContainerElement extends HtmlElement with OrderableContainer {
    OrderableContainerElement.created(): super.created();
}


void registerOrderableContainerElement() {
    document.registerElement('orderable-container', OrderableContainerElement);
}