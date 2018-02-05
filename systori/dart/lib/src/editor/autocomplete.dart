import 'dart:html';
import 'dart:async';
import 'model.dart';
import 'package:systori/inputs.dart';


Autocomplete autocomplete;


typedef void AutocompleteSelectionCallback(String id);
typedef Map<String,String> MakeCriteria();

class AutocompleteKeyboardHandler extends KeyboardHandler {

    final Model model;
    final MakeCriteria makeCriteria;
    final AutocompleteSelectionCallback autocompleteSelection;

    AutocompleteKeyboardHandler(this.model, this.makeCriteria, this.autocompleteSelection);

    bool get canAutocomplete => model.hasNoPK && model.hasNoChildModels;

    @override
    onFocusEvent(Input input) {
        if (!canAutocomplete) return;
        autocomplete.criteria = makeCriteria();
        autocomplete.criteria['model_type'] = this.model.type;
        autocomplete.reposition(input);
    }

    @override
    onInputEvent(Input input) {
        if (!canAutocomplete) return true;
        autocomplete.criteria['terms'] = input.text;
        autocomplete.search();
    }

    @override
    onBlurEvent(Input input) {
        autocomplete.criteria = {};
        autocomplete.hide();
    }

    @override
    bool onKeyDownEvent(KeyEvent e, Input input) {
        if (!canAutocomplete) return false;
        switch(e.keyCode) {
            case KeyCode.UP:
                e.preventDefault();
                autocomplete.handleUp();
                return true;
            case KeyCode.DOWN:
                e.preventDefault();
                autocomplete.handleDown();
                return true;
            case KeyCode.ENTER:
                String id = autocomplete.handleEnter();
                if (id != null) {
                    e.preventDefault();
                    autocompleteSelection(id);
                } else {
                    // autocomplete is active but nothing was selected
                    // allow event propagation
                    return false;
                }
                return true;
            case KeyCode.ESC:
                e.preventDefault();
                autocomplete.handleEscape();
                return true;
            default:
                return false;
        }
    }

}


class Autocomplete extends HtmlElement {

    Autocomplete.created(): super.created();

    Input input;
    Map<String,String> criteria;
    List<StreamSubscription> eventStreams;

    int offsetFromTop;

    bool searching = false;
    bool searchRequested = false;

    reposition(Input input) {
        this.input = input;
        input.insertAdjacentElement('afterEnd', this);
        offsetFromTop = input.offsetHeight;
        style.top = '${offsetFromTop}px';
        style.left = '0px';
        //style.left = '${input.offsetLeft}px';
    }

    hide() {
        input = null;
        setInnerHtml('');
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
            for (Map row in result) {
                html.write('<div data-id="');
                html.write(row['id']);
                html.write('"><h2>');
                html.write(row['match_name']);
                html.write('</h2><p>');
                html.write(row['match_description']);
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
        try {
            var current = this.querySelector('.active');
            if (current == null) return;
            var previous = current.previousElementSibling;
            if (previous != null) {
                select(current, previous);
            }
        } catch(exception, stackTrace) { print("exception appeared editor handleUp()."); }
    }

    handleDown() {
        try {
            var current = this.querySelector('.active');
            if (current == null) {
                select(current, children.first);
            } else {
                var next = current.nextElementSibling;
                if (next != null) {
                select(current, next);
                }
            }
        } catch(exception, stackTrace) { print("exception appeared editor handleDown()."); }
    }

    select(DivElement previous, DivElement current) {

        if (previous != null) {
            var previousInfo = previous.querySelector(':scope>.autocomplete-info');
            if (previousInfo != null) {
                previousInfo.style.visibility = 'hidden';
            }
        }

        children.forEach((e) => e.classes.clear());
        current.classes.add('active');
        style.top = "${offsetFromTop - current.offsetTop}px";

        DivElement info = current.querySelector(':scope>.autocomplete-info');
        if (info != null) {
            info.style.visibility = 'visible';
        } else {
            info = document.createElement('div');
            info.classes.add('autocomplete-info');
            info.text = '...';
            current.children.add(info);
            repository.info(criteria['model_type'], current.dataset['id']).then((Map data) {
                info.setInnerHtml(
                    criteria['model_type'] == 'task' ?
                        createTaskInfo(data) :
                        createGroupInfo(data),
                    treeSanitizer: NodeTreeSanitizer.trusted
                );
                /* make sure user hasn't selected some other item while
                   we were waiting on the server before making this visible
                */
                if (current == this.querySelector('.active')) {
                    info.style.visibility = 'visible';
                }
            });
        }
    }

    String createGroupInfo(Map data) {
        var html = new StringBuffer();
        html.write("<p>${data['name']} - <b>${data['total']}</b></b></p>");
        html.write("<p>${data['description']}</p>");
        return html.toString();
    }

    String createTaskInfo(Map data) {
        var html = new StringBuffer();
        html.write("<table>");
        html.write("<tr style='border-bottom: 1px solid gray;'><td colspan='2'>Project #${data['project_id']}</td>");
        html.write("<td class='info-decimal info-qty' nowrap>${data['qty']} ${data['unit']}</td>");
        html.write("<td class='info-decimal info-price'>${data['price']}</td>");
        html.write("<td class='info-decimal info-total'>${data['total']}</td>");
        html.write("</tr>");
        html.write("<tr><td colspan='5'><b>${data['name']}</b></td></tr>");
        html.write("<tr><td colspan='5'>${data['description']}</td></tr>");
        html.write("<tr style='border-bottom: 1px solid gray;'><td colspan='5'>&nbsp;</td></tr>");
        html.write("<tr><td colspan='4'></td></tr>");
        for (Map li in data['lineitems']) {
            html.write("<tr>");
            if (li['name'].length > 47) {
                html.write("<td colspan='5'>${li['name']}</td>");
                html.write("</tr><tr><td colspan='2'>&nbsp;</td>");
            } else {
                html.write("<td colspan='2'>${li['name']}</td>");
            }
            html.write("<td class='info-decimal info-qty' nowrap>${li['qty']} ${li['unit']}</td>");
            html.write("<td class='info-decimal info-price'>${li['price']}</td>");
            html.write("<td class='info-decimal info-total'>${li['total']}</td>");
            html.write("</tr>");
        }
        html.write("</table>");
        return html.toString();
    }

    handleEscape() => hide();

    handleEnter() {
        var current = this.querySelector('.active');
        if (current != null) {
            return current.dataset['id'];
        }
    }

}
