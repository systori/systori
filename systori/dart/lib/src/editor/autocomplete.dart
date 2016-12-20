import 'dart:html';
import 'dart:async';
import 'editor.dart';
import 'model.dart';


abstract class AutocompleteReceiver {
    Input name;
    onAutocompleteFinished(String id);
}


class Autocomplete extends HtmlElement {

    Autocomplete.created(): super.created();

    AutocompleteReceiver boundReceiver;
    Map<String,String> extraCriteria;
    List<StreamSubscription> eventStreams;

    int offsetFromTop;

    bool searching = false;
    bool searchRequested = false;

    bind(AutocompleteReceiver receiver, Map<String,String> criteria) {

        if (boundReceiver != null) {
            eventStreams.forEach((s) => s.cancel());
        }

        boundReceiver = receiver;
        extraCriteria = criteria;

        var input = receiver.name;
        input.insertAdjacentElement('afterEnd', this);
        eventStreams = <StreamSubscription>[
            input.onKeyDown.listen(handleKey),
            input.onBlur.listen(handleBlur)
        ];

        offsetFromTop = input.offsetHeight;
        style.top = '${offsetFromTop}px';
        style.left = '${input.offsetLeft}px';

    }

    search() async {
        if (searching) {
            searchRequested = true;
            return;
        }
        try {
            var criteria = {
                'terms': boundReceiver.name.text
            };
            criteria.addAll(extraCriteria);
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

    handleKey(KeyboardEvent e) {
        switch(e.keyCode) {
            case KeyCode.UP:
                e.preventDefault();
                handleUp();
                break;
            case KeyCode.DOWN:
                e.preventDefault();
                handleDown();
                break;
            case KeyCode.ENTER:
                e.preventDefault();
                handleEnter();
                break;
            default:
                search();
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
        if (current != null)
            boundReceiver.onAutocompleteFinished(current.dataset['id']);
    }

    handleBlur([Event _]) {
        style.visibility = 'hidden';
    }

}
