import 'dart:html';
import 'dart:async';
import 'editor.dart';
import 'model.dart';


abstract class AutocompleteReceiver {
    Input name;
    onAutocompleteFinished(int id);
}


class Autocomplete extends HtmlElement {

    Autocomplete.created(): super.created();

    Input boundInput;
    Map<String,String> extraCriteria;
    List<StreamSubscription> eventStreams;

    bool searching = false;
    bool searchRequested = false;

    bind(AutocompleteReceiver receiver, Map<String,String> criteria) {
        if (boundInput != null) {
            eventStreams.forEach((s) => s.cancel());
        }
        boundInput = receiver.name;
        boundInput.insertAdjacentElement('afterEnd', this);
        extraCriteria = criteria;
        eventStreams = <StreamSubscription>[
            boundInput.onKeyUp.listen(search),
            boundInput.onBlur.listen(blur)
        ];
        style.top = boundInput.offsetHeight.toString()+'px';
        style.left = boundInput.offsetLeft.toString()+'px';
    }

    search([KeyboardEvent e]) async {
        if (searching) {
            searchRequested = true;
            return;
        }
        try {
            var criteria = {
                'terms': boundInput.text
            };
            criteria.addAll(extraCriteria);
            var result = await repository.search(criteria);
            var html = new StringBuffer();
            for (List row in result) {
                html.write('<h4>');
                html.write(row[1]);
                html.write('</h4>');
                html.write(row[2]);
                html.write('<br />');
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

    blur([Event _]) {
        style.visibility = 'hidden';
    }

}
