import 'dart:html';
import 'dart:async';
import 'editor.dart';
import 'model.dart';


Autocomplete autocomplete;


typedef void AutocompleteSelectionCallback(String id);

class AutocompleteKeyboardHandler implements KeyboardHandler {

    Model model;
    Map<String,String> criteria;
    AutocompleteSelectionCallback autocompleteSelection;

    AutocompleteKeyboardHandler(this.model, this.criteria, this.autocompleteSelection) {
        criteria['model_type'] = this.model.type;
    }

    onFocusEvent(Input input) {
        autocomplete.criteria = criteria;
        autocomplete.reposition(input);
    }

    onBlurEvent(Input input) {
        autocomplete.criteria = {};
        autocomplete.hide();
    }

    bool onKeyEvent(KeyEvent e, Input input) {
        switch(e.keyCode) {
            case KeyCode.UP:
                autocomplete.handleUp();
                return false;
            case KeyCode.DOWN:
                autocomplete.handleDown();
                return false;
            case KeyCode.ENTER:
                String id = autocomplete.handleEnter();
                if (id != null) autocompleteSelection(id);
                return false;
            default:
                autocomplete.criteria['terms'] = input.text;
                autocomplete.search();
                return false;
        }
        return true;
    }

}


class Autocomplete extends HtmlElement {

    Autocomplete.created(): super.created();

    Map<String,String> criteria;
    List<StreamSubscription> eventStreams;

    int offsetFromTop;

    bool searching = false;
    bool searchRequested = false;

    reposition(Input input) {
        input.insertAdjacentElement('afterEnd', this);
        offsetFromTop = input.offsetHeight;
        style.top = '${offsetFromTop}px';
        style.left = '${input.offsetLeft}px';
    }

    hide() {
        style.visibility = 'hidden';
    }

    search() async {
        if (searching) {
            searchRequested = true;
            return;
        }
        searching = true;
        try {
            var result = await repository.search(criteria);
            var html = new StringBuffer();
            for (List row in result) {
                html.write('<div data-id="');
                html.write(row[0]);
                html.write('"><div>');
                html.write(row[1]);
                html.write('</div><p>');
                html.write(row[2]);
                html.write('</p></div>');
            }
            setInnerHtml(
                html.toString(),
                treeSanitizer: NodeTreeSanitizer.trusted
            );
            style.visibility = 'visible';
        } finally {
            searching = false;
            if (searchRequested) {
                searchRequested = false;
                search();
            }
        }
    }

    handleUp() {
        var current = this.querySelector('.active');
        if (current == null) return;
        var previous = current.previousElementSibling;
        if (previous != null) {
            children.forEach((e) => e.classes.clear());
            previous.classes.add('active');
            style.top = "${offsetFromTop - previous.offsetTop}px";
        }
    }

    handleDown() {
        var current = this.querySelector('.active');
        if (current == null) {
            this.children.first.classes.add('active');
        } else {
            var next = current.nextElementSibling;
            if (next != null) {
                children.forEach((e) => e.classes.clear());
                next.classes.add('active');
                this.style.top = "${offsetFromTop - next.offsetTop}px";
            }
        }
    }

    handleEnter() {
        var current = this.querySelector('.active');
        if (current != null) {
            return current.dataset['id'];
        }
    }

}
