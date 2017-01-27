import 'dart:html';

class Scaffolding {
    Element element;
    String html;
    Scaffolding(this.element) {
        html = element.innerHtml;
    }
    reset() {
        /*
        * Be careful selecting which element to be the scaffold. The innerHtml
        * has be valid HTML on its own.
        * For example, if you use a table as the scaffold then you will end up with
        * tbody/tr's in innerHtml. This innerHtml cannot be independently instantiated
        * in a DocumentFragment because with the parent <table> it's not valid HTML.
        * You will need to create an out <div> containing the <table> and then make
        * this <div> be your root scaffold.
        * */
        /* There appears to be a bug when setting innerHtml directly on the main
         * document. The lifecycle of custom elements does not work properly.
         * Inflating the elements in a document fragment and then settings that on main
         * document seems to work. */
        var frag = document.createDocumentFragment();
        frag.setInnerHtml(html, treeSanitizer: NodeTreeSanitizer.trusted);
        element.children.clear();
        element.children.addAll(frag.children);
    }
}
