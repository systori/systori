import 'dart:html';

class Scaffolding {
    Element element;
    String html;
    Scaffolding(this.element) {
        html = element.innerHtml;
    }
    reset() {
        /* There appears to be a bug when setting innerHtml directly on the main
         * document. The lifecycle of custom elements does not work properly.
         * Inflating the elements in a document fragment and then settings that on main
         * document seems to work. */
        var frag = document.createDocumentFragment();
        frag.setInnerHtml(html, treeSanitizer: NodeTreeSanitizer.trusted);
        element.children.clear();
        element.append(frag.children[0]);
    }
}
