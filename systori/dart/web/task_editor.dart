import 'dart:html';
import 'dart:async';
import 'dart:convert';
import 'package:intl/intl.dart';
import 'package:collection/collection.dart';
import 'common.dart';


final Repository repository = new Repository();

enum InputMode {
    TASK,
    LINEITEM
}

InputMode INPUT_MODE = InputMode.LINEITEM;


DocumentFragment stringToDocumentFragment(html) {
    var tmp = document.createDocumentFragment();
    tmp.setInnerHtml(html, validator:
    new NodeValidatorBuilder.common()
        ..allowCustomElement('ubr-taskgroup', attributes: ['data-pk'])
        ..allowCustomElement('ubr-task', attributes: ['data-pk'])
        ..allowCustomElement('ubr-taskinstance', attributes: ['data-pk'])
        ..allowCustomElement('ubr-lineitem', attributes: ['data-pk'])
        ..allowCustomElement('ubr-autocomplete', attributes: ['data-pk'])
        ..allowElement('div', attributes: ['contenteditable', 'placeholder', 'data-pk'])
        ..allowElement('br')
    );
    return tmp;
}


class Repository {

    Map<String, String> headers;

    Repository() {
        var csrftoken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
        headers = {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        };
    }

    Future<int> insert(String type, Map<String, String> data) {
        var wait_for_response = HttpRequest.request(
                "/api/v1/${type}/",
                method: "POST",
                requestHeaders: headers,
                sendData: JSON.encode(data)
        );

        var result = new Completer<int>();
        wait_for_response.then((response) {
            var location = response.responseHeaders['location'];
            var id_match = new RegExp(r'/(\d+)/$').firstMatch(location);
            if (id_match != null) {
                var id = int.parse(id_match.group(1));
                result.complete(id);
            } else {
                result.completeError("No id in response.");
            }
        }, onError: result.completeError);
        return result.future;
    }

    Future<bool> update(String type, int id, Map<String, String> data) {
        var wait_for_response = HttpRequest.request(
                "/api/v1/${type}/${id}/",
                method: "PUT",
                requestHeaders: headers,
                sendData: JSON.encode(data)
        );

        var result = new Completer<int>();
        wait_for_response.then((response) {
            if (response.status == 204) {
                result.complete(true);
            } else {
                result.completeError("Wrong status returned from server.");
            }
        }, onError: result.completeError);
        return result.future;
    }

    Future<bool> delete(String type, int id) {
        var wait_for_response = HttpRequest.request(
                "/api/v1/${type}/${id}/",
                method: "DELETE",
                requestHeaders: headers
        );

        var result = new Completer<int>();
        wait_for_response.then((response) {
            if (response.status == 204) {
                result.complete(true);
            } else {
                result.completeError("Wrong status returned from server.");
            }
        }, onError: result.completeError);
        return result.future;
    }

    Future<String> autocomplete(String type, String query) {
        var encoded_query = Uri.encodeQueryComponent(query);
        var wait_for_response = HttpRequest.request(
                "/api/v1/${type}/autocomplete/?query=$encoded_query",
                method: "GET", requestHeaders: headers
        );

        var result = new Completer<List>();
        wait_for_response.then((response) {
            result.complete(response.responseText);
        }, onError: result.completeError);
        return result.future;
    }

    Future<String> clone(String type, String id, Map<String, String> data) {
        var wait_for_response = HttpRequest.request(
                "/api/v1/${type}/${id}/clone/",
                method: "POST",
                requestHeaders: headers,
                sendData: JSON.encode(data)
        );

        var result = new Completer<String>();
        wait_for_response.then((response) {
            result.complete(response.responseText);
        }, onError: result.completeError);
        return result.future;
    }

}


class AutoComplete extends HtmlElement {

    final int offsetFromTop = 20;

    StreamController<Map> controller = new StreamController<Map>();

    get onSelected => controller.stream;

    get isActive => style.display == 'block';

    get hasSelection => this.querySelector('.active') != null;

    AutoComplete.created() : super.created();

    handleResults(String html) {
        if (html.trim().isEmpty) {
            style.display = 'none';
            return;
        }
        children = stringToDocumentFragment(html).children;
        style.top = "${offsetFromTop}px";
        style.display = 'block';
    }

    handleUp() {
        var current = this.querySelector('.active');
        if (current == null) return;
        var previous = current.previousElementSibling;
        if (previous != null) {
            children.forEach((e) => e.classes.clear());
            previous.classes.add('active');
            this.style.top = "${previous.offsetTop * -1 + offsetFromTop}px";
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
                this.style.top = "${next.offsetTop * -1 + offsetFromTop}px";
            }
        }
    }

    handleEnter() {
        var current = this.querySelector('.active');
        if (current != null)
            handleSelection(current);
    }

    handleSelection(DivElement current) {
        controller.add({
            'id': current.dataset['pk'],
            'name': current.text
        });
        handleBlur();
    }

    handleBlur([event]) {
        style.display = 'none';
    }

}


abstract class UbrElement extends HtmlElement {
    int pk;

    String get object_name => nodeName.toLowerCase().substring(4);

    String child_element;

    // defined in subclasses
    String get child_name => child_element.substring(4);

    int get parent_pk => (parent as UbrElement).pk;

    String get parent_name => (parent as UbrElement).object_name;

    String get code => dataset['code'];

    int get child_zfill;

    int get child_offset => 0;

    double get total => 0.0;

    set total(double calculated) => dataset['total'] = CURRENCY.format(calculated);

    UbrElement.created() : super.created() {
        if (dataset.containsKey('pk'))
            pk = int.parse(dataset['pk']);
    }

    recalculate_code() {
        ElementList<EditableElement> items = this.querySelectorAll(child_element);

        for (int i = 0; items.length > i; i++) {
            var new_code = (i + 1 + child_offset).toString().padLeft(child_zfill, '0');
            items[i].code_view.text = "${code}.${new_code}";
        }
    }

}


class JobElement extends UbrElement {
    final child_element = "ubr-taskgroup";

    DivElement total_view;
    DivElement total_gross_view;
    double tax_rate;

    int get child_zfill => int.parse(dataset['taskgroup-zfill']);

    int get child_offset => int.parse(dataset['taskgroup-offset']);

    double get total => total_view != null ? parse_currency(total_view.text) : 0.0;
    double get total_gross => total_gross_view != null ? parse_currency(total_gross_view.text) : 0.0;

    set total(double calculated) => total_view.text = CURRENCY.format(calculated);
    set total_gross(double calculated) => total_gross_view.text = CURRENCY.format(calculated);

    JobElement.created(): super.created() {
        total_view = this.querySelector(".job-total");
        total_gross_view = this.querySelector(".job-total-gross");
        tax_rate = double.parse(total_gross_view.dataset['taxRate']);
    }

    update_totals() {
        total = document.querySelectorAll(child_element)
            .map((e) => e.total)
            .fold(0, (a, b) => a + b);
        total_gross = total + total * tax_rate;
    }
}


abstract class EditableElement extends UbrElement {

    DivElement code_view;
    DivElement name_view;
    DivElement description_view;
    DivElement qty_view;
    DivElement unit_view;
    DivElement price_view;
    DivElement total_view;

    DivElement hint;

    ElementList<DivElement> input_views;
    Map<String, SpanElement> toggle_views = {};

    double get total => total_view != null ? parse_currency(total_view.text) : 0.0;

    set total(double calculated) => total_view.text = CURRENCY.format(calculated);

    String get code => code_view.text;

    int get child_zfill => null;

    List<String> previous_values = [];
    bool started = false;

    // prevents unfocus from being called
    // when we have already handled the
    // situation of stopping this editor
    List<StreamSubscription<Event>> streams = [];

    AutoComplete autocompleter;

    EditableElement.created() : super.created() {

        if (children.isEmpty) {
            var template = document.querySelector('#${object_name}-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }

        if (this.querySelector(":scope>${child_element}") == null) {
            classes.add('empty');
        }

        code_view = this.querySelector(":scope>.editor .code");
        name_view = this.querySelector(":scope>.editor .name");
        description_view = this.querySelector(":scope>.editor .description");
        qty_view = this.querySelector(":scope>.editor .qty");
        unit_view = this.querySelector(":scope>.editor .unit");
        price_view = this.querySelector(":scope>.editor .price");
        total_view = this.querySelector(":scope>.editor .total");

        input_views = this.querySelectorAll(':scope>.editor [contenteditable]');
        streams.add(input_views.onBlur.listen(unfocus));
        input_views.onKeyDown.listen(handle_input);
        input_views.onKeyUp.listen(handle_input_key_up);
        input_views.onFocus.listen((MouseEvent event) {
            if (!started)
                start(focus: false);
        });

        input_views.forEach((Element e) {

            // we listen for paste events and try to clean up the pasted data
            e.onPaste.listen((ClipboardEvent event) {

                event.preventDefault();

                var data = '';

                if (event.clipboardData.types.contains('text/html')) {

                    data = event.clipboardData.getData('text/html')

                        // div's and p's usually start a new line so we'll convert them to a <br>
                        .replaceAll(new RegExp(r'<div[^>]*>', caseSensitive: false), '<br>')
                        .replaceAll(new RegExp(r'<p[^>]*>', caseSensitive: false), '<br>')

                        // cleanup any <br /> or <BR> to <br> for consistency
                        .replaceAll(new RegExp(r'<br[^>]*>', caseSensitive: false), '<br>')

                        // remove everything else
                        .replaceAll(new RegExp(r'<(?!br).*?>', caseSensitive: false), '');

                } else {

                    data = event.clipboardData.getData('text/plain');

                }

                // update the input with valid value
                e.setInnerHtml(data,
                    validator: new NodeValidatorBuilder.common()..allowElement('br')
                );

            });
        });

        // recalculate totals when these views are changed
        [qty_view, price_view].where((v) => v != null)
        .forEach((DivElement view) {
            view.onKeyUp.listen((KeyboardEvent event) {
                this.update_totals();
            });
        });

        // select the entire contents of the view when these views are focused
        [qty_view, price_view, unit_view].where((v) => v != null)
        .forEach((DivElement view) {
            view.onFocus.listen((FocusEvent event) {
                /* This timer solves an annoying situation when user clicks
         * on an input field and two events are fired:
         *   1) onFocus is fired first and the text is selected. So far good.
         *   2) Immediately after onFocus, the onClick event is fired. But the onClick event
         *      default behavior is to place a carret somewhere in the text. This causes the
         *      selection we made in onFocus to be un-selected. :-(
         * The solution is to set a timer that will delay selecting text
         * until after onClick is called. It's a hack but it works.
         */
                new Timer(new Duration(milliseconds: 1), () {
                    window.getSelection().selectAllChildren(event.target);
                });
            });
        });

        // move carret to the end of content when these views are focused
        [name_view, description_view].where((v) => v != null)
        .forEach((DivElement view) {
            view.onFocus.listen((FocusEvent event) {
                window.getSelection()
                    ..selectAllChildren(event.target)
                    ..collapseToEnd();
            });
        });

        hint = this.querySelector(":scope>.editor>.editor-hint");
    }

    attached() {
       offset_scroll();
    }

    offset_scroll(){
        this.scrollIntoView(ScrollAlignment.TOP);
        window.scrollBy(0,-280);
    }

    use_autocompleter() {
        var editor_row = this.querySelector(":scope>.editor>.editor-row");
        autocompleter = document.createElement('ubr-autocomplete');
        editor_row.insertAdjacentElement('afterend', autocompleter);
        autocompleter.onSelected.listen(autocomplete_option_selected);
        name_view.onBlur.listen(autocompleter.handleBlur);
        streams.add(name_view.onKeyUp.listen(autocomplete));
    }

    bool truthy(String toggle_name) =>
    toggle_views[toggle_name].classes.contains('True');

    bool toggle(String toggle_name) {
        var classes = toggle_views[toggle_name].classes;
        if (classes.contains('True')) {
            classes.remove('True');
            classes.add('False');
            return false;
        } else {
            classes.remove('False');
            classes.add('True');
            return true;
        }
    }

    add_toggle(String toggle_name) {
        SpanElement span = this.querySelector(":scope>.editor .$toggle_name");
        toggle_views[toggle_name] = span;
        span.onClick.listen((MouseEvent event) {
            toggle(toggle_name);
            save();
            update_totals();
        });
    }

    List _editable_values() {
        return input_views.map((e) => e.innerHtml).toList();
    }

    bool is_modified() {
        return !const ListEquality().equals(previous_values, _editable_values());
    }

    bool is_name_blank() {
        return name_view.text.length == 0;
    }

    bool is_blank() {
        return this.is_name_blank() && pk == null;
    }

    bool can_delete() {
        return true;
    }

    void handle_down_key(KeyboardEvent event) {
        this.stop_n_save();
        this.next();
        this.cleanup();
        this.scrollIntoView();
    }

    void handle_up_key(KeyboardEvent event) {
        this.stop_n_save();
        this.previous();
        this.cleanup();
        this.scrollIntoView();
    }

    void handle_enter_key(KeyboardEvent event) {
        if (event.shiftKey) {
            event.preventDefault();

            if (is_blank()) {
                this.new_parent_sibling();
                return;
            } else {
                this.stop_n_save();
            }

            if (event.ctrlKey) {
                this.new_parent_sibling();
                return;
            }

            if (INPUT_MODE == InputMode.TASK && object_name == 'task') {
                this.new_sibling();
            } else if (child_element != null) {
                if (INPUT_MODE == InputMode.LINEITEM && object_name == 'task') {
                    if (event.altKey) {
                        this.new_child();
                    } else {
                        var children = this.querySelectorAll(this.child_element);
                        if (children.length > 0) {
                            children.last.new_child();
                        } else {
                            this.new_child();
                        }
                    }
                } else {
                    this.new_child();
                }
            } else {
                this.new_sibling();
            }
        }
    }

    void handle_esc_key(KeyboardEvent event) {
    }

    void handle_delete_key(KeyboardEvent event) {
        if (event.shiftKey) {
            if (!this.can_delete()) return;
            event.preventDefault();
            this.delete();
            this.stop();
            this.next(include_children: false) || this.previous();

            var saved_parent = this.parent;

            this.remove();

            if (saved_parent.querySelector(":scope>${nodeName}") == null) {
                saved_parent.classes.add('empty');
            }
        }

    }

    void handle_input(KeyboardEvent event) {

        switch (event.keyCode) {

            case KeyCode.DOWN:
                event.preventDefault();
                if (autocompleter != null && autocompleter.isActive) {
                    autocompleter.handleDown();
                } else {
                    this.handle_down_key(event);
                }

                break;

            case KeyCode.UP:
                event.preventDefault();
                if (autocompleter != null && autocompleter.isActive) {
                    autocompleter.handleUp();
                } else {
                    this.handle_up_key(event);
                }
                break;

            case KeyCode.ENTER:
                if (autocompleter != null && autocompleter.isActive && autocompleter.hasSelection) {
                    event.preventDefault();
                    this.stop();
                    autocompleter.handleEnter();

                } else {
                    this.handle_enter_key(event);
                }
                break;

            case KeyCode.ESC:
                if (autocompleter != null) {
                    event.preventDefault();
                    autocompleter.handleBlur();
                } else {
                    this.handle_esc_key(event);
                }
                break;

            case KeyCode.DELETE:
                this.handle_delete_key(event);
                break;
        }
    }

    void handle_input_key_up(KeyboardEvent event) {
        this._refresh_hint_context();
    }

    void autocomplete(KeyboardEvent event) {
        switch (event.keyCode) {
            case KeyCode.UP:
            case KeyCode.DOWN:
            case KeyCode.ENTER:
            case KeyCode.DELETE:
            case KeyCode.LEFT:
            case KeyCode.RIGHT:
            case KeyCode.ESC:
                break;
            default:
                var search = name_view.text.trim();
                if (search.length > 1) {
                    repository.autocomplete(object_name, search).then((data) {
                        autocompleter.handleResults(data);
                    });
                } else {
                    autocompleter.handleBlur();
                }
        }
    }

    void autocomplete_option_selected(Map selection) {
        name_view.text = selection['name'];
        var create_data = toMap();
        var data = {
            'target': create_data[parent_name],
            'pos': create_data['order']
        };
        repository.clone(object_name, selection['id'], data).then((resp) {
            var frag = stringToDocumentFragment(resp);
            var idx = parent.children.indexOf(this);
            var this_parent = this.parent;
            replaceWith(frag.children[0]);
            (this_parent.children[idx] as EditableElement).start();
        });
    }

    void unfocus(event) {
        new Timer(new Duration(milliseconds: 500), () {
            if (document.activeElement != this &&
            !input_views.contains(document.activeElement)) {
                stop_n_save();
                cleanup();
            }
        });
    }

    Map<String, String> toMap() {
        var data = {
            parent_name: "/api/v1/${parent_name}/${parent_pk}/"
        };
        input_views.forEach((Element e) {
            data[e.className] = e.innerHtml

            .replaceAll('<div>', '<br />')
            .replaceAll('</div>', '')

            // can't support formatting yet
            .replaceAll(new RegExp(r'<\/?i>'), '')
            .replaceAll(new RegExp(r'<\/?b>'), '')

            .replaceAll(new RegExp(r'<\/?span.*?>'), '')

            .replaceAll('<br>', '<br />');

        });
        toggle_views.forEach((key, _) {
            data[key] = truthy(key);
        });
        var child_elements = parent.querySelectorAll(this.nodeName);
        var order = 0;
        for (; child_elements.length > order; order++) {
            if (child_elements[order] == this) break;
        }
        data['order'] = order;
        return data;
    }

    void start({bool focus: true}) {
        previous_values = _editable_values();
        streams.forEach((s) => s.resume());
        if (focus) {
            name_view.focus();
        }
        classes.add('focused');
        started = true;
        this.show_hint();
    }

    void stop_n_save() {
        stop();
        save();
    }

    void stop() {
        this.hide_hint();
        streams.forEach((s) => s.pause());
        classes.remove('focused');
        started = false;
    }

    void cleanup() {
        if (is_blank() && can_delete()) {
            UbrElement parent_cached = parent;
            remove();
            parent_cached.recalculate_code();
            if (parent_cached.querySelector(":scope>${nodeName}") == null) {
                parent_cached.classes.add('empty');
            }
        }
    }

    void save({bool force_empty: false}) {
        if (is_modified() && (force_empty || !is_blank())) {
            var data = toMap();
            if (pk != null) {
                repository.update(object_name, pk, data);
            } else {
                repository.insert(object_name, data).then((new_pk) {
                    pk = new_pk;
                    after_create();
                });
            }
        }
    }

    void after_create() {
    }

    void delete() {
        if (pk != null) {
            repository.delete(object_name, pk);
        }
    }

    bool previous({bool include_parent: true}) {
        var match;

        // try siblings
        match = this.previousElementSibling;
        if (match is EditableElement) {
            while (true) {
                List subelements = match.child_element != null ? match.querySelectorAll(match.child_element) : [];
                if (subelements.isEmpty) break;
                match = subelements.last as EditableElement;
            }
            match.start();
            return true;
        }

        if (include_parent) {
            // try parent
            match = this.parent;
            if (match is TaskInstanceElement && match.parent.querySelectorAll(match.parent.child_element).length == 1) {
                match.previous();
                return true;
            } else if (match is EditableElement) {
                match.start();
                return true;
            }
        }

        return false;
    }

    bool next({bool include_children: true}) {
        var match;

        if (include_children) {
            // try child elements
            if (child_element != null) {
                match = this.querySelector(child_element);
                if (match is TaskInstanceElement && match.parent.querySelectorAll(match.parent.child_element).length == 1) {
                    match.next();
                    return true;
                } else if (match is EditableElement) {
                    match.start();
                    return true;
                }
            }
        }

        // now try siblings
        match = this.nextElementSibling;
        if (match is EditableElement) {
            match.start();
            return true;
        }

        // visit the ancestors
        var ancestor = parent;
        while (ancestor is EditableElement) {
            var sibling = ancestor.nextElementSibling;
            if (sibling is EditableElement) {
                sibling.start();
                return true;
            }
            ancestor = ancestor.parent;
        }

        return false;

    }

    void new_child() {
        EditableElement item = document.createElement(child_element);
        append(item);
        recalculate_code();
        classes.remove('empty');
        item.start();
    }

    void new_sibling() {
        EditableElement item = document.createElement(nodeName);
        insertAdjacentElement('afterend', item);
        (parent as UbrElement).recalculate_code();
        item.start();
    }

    void new_parent_sibling() {
        (parent as EditableElement).new_sibling();
    }

    update_totals();

    children_total_sum() {
        var items = this.querySelectorAll(child_element).map((e) => e.total);
        return items.fold(0, (a, b) => a + b);
    }

    void hide_editor() {
        var editor = this.querySelector(":scope>.editor");
        editor.classes.add('hidden');
    }

    void show_editor() {
        var editor = this.querySelector(":scope>.editor");
        editor.classes.remove('hidden');
    }

    void show_hint() {
        if (hint != null) {
            hint.style.display = 'block';
            this._refresh_hint_context();
        }
    }

    void hide_hint() {
        if (hint != null) {
            hint.style.display = 'none';
        }
    }

    void _refresh_hint_context() {
        var visible, hidden;
        if (this.is_name_blank()) {
            visible = hint.querySelectorAll('.blank');
            hidden = hint.querySelectorAll('.non-blank');
        }
        else {
            visible = hint.querySelectorAll('.non-blank');
            hidden = hint.querySelectorAll('.blank');
        }
        visible.forEach((e) => e.classes.remove('hidden'));
        hidden.forEach((e) => e.classes.add('hidden'));
    }
}


class TaskGroupElement extends EditableElement {
    final child_element = "ubr-task";

    int get child_zfill => int.parse(parent.dataset['task-zfill']);

    TaskGroupElement.created(): super.created() {
        if (pk == null) {
            use_autocompleter();
        }
    }

    bool can_delete() {
        return parent.children.length > 1;
    }

    update_totals() {
        total = this.querySelectorAll(child_element)
            .where((e) => e.truthy('is_optional') == false)
            .map((e) => e.total)
            .fold(0, (a, b) => a + b);
        (parent as EditableElement).update_totals();
    }

}


class TaskElement extends EditableElement {
    final child_element = "ubr-taskinstance";

    TaskElement.created(): super.created() {
        if (pk == null) {
            use_autocompleter();
        }
        add_toggle('is_optional');
    }

    Map<String, String> toMap() {
        var data = super.toMap();
        data['qty'] = parse_decimal(qty_view.text);
        return data;
    }

    recalculate_code() {
    }

    update_totals() {
        var qty = parse_decimal(qty_view.text);
        var price = children_total_sum();
        price_view.text = CURRENCY.format(price);
        total = qty * price;
        (parent as EditableElement).update_totals();
    }

    after_create() {
        if (INPUT_MODE == InputMode.LINEITEM)
            new_child();
    }

    new_child() {
        //
        // This new_child handles the following two use cases:
        //
        // 1. When a new task has just been created:
        //    a. Create and save a new Task Instance.
        //    b. Create the first Line Item.
        //    c. Start editing the first line item, bypassing the task instance.
        //
        // 2. When user is intentionally creating Task Instances:
        //    a. Follow the normal new_child() behavior.
        //

        if (pk == null) {
            // Wait for after_create() to call this method again.
            return;
        }

        // Use Case 1:
        if (this.querySelectorAll(child_element).isEmpty) {

            TaskInstanceElement item = document.createElement(child_element);
            append(item);

            var data = item.toMap();
            data['selected'] = true;
            repository.insert(child_name, data).then((new_pk) {
                item.pk = new_pk;
                item.new_child(); // <-- starts a new line item
            });

            classes.remove('empty');

        // Use Case 2:
        } else {
            super.new_child();
        }
    }

    void new_sibling() {
        super.new_sibling();
    }

    children_total_sum() {
        TaskInstanceElement first_child = this.querySelector(child_element);
        if (first_child != null)
            return first_child.total;
        return 0.0;
    }

}


class TaskInstanceElement extends EditableElement {
    final child_element = "ubr-lineitem";

    double get total => children_total_sum();

    TaskInstanceElement.created(): super.created() {
    }

    recalculate_code() {
    }

    update_totals() {
        (parent as EditableElement).update_totals();
    }

    bool can_delete() {
        return this.parent.querySelectorAll((this.parent as EditableElement).child_element).length > 1;
    }
}

class LineItemElement extends EditableElement {

    LineItemElement.created(): super.created() {
        add_toggle('is_flagged');
    }

    Map<String, String> toMap() {
        var data = super.toMap();
        data['unit_qty'] = parse_decimal(qty_view.text).toString();
        data['price'] = parse_decimal(price_view.text).toString();
        return data;
    }

    recalculate_code() {
    }

    update_totals() {
        var qty = parse_decimal(qty_view.text);
        var price = parse_decimal(price_view.text);
        total = qty * price;
        (this.parent as EditableElement).update_totals();
    }

    void new_parent_sibling() {
        (parent.parent as EditableElement).new_sibling();
    }

    void handle_delete_key(event) {
        var saved_parent = this.parent;
        super.handle_delete_key(event);
        saved_parent.update_totals();

        if (event.shiftKey && saved_parent.can_delete() && saved_parent.classes.contains('empty')) {
            saved_parent.delete();
            saved_parent.remove();
        }
    }

}


setup_input_mode_buttons() {
    querySelector('#input-task-mode').onClick.listen((_) => INPUT_MODE = InputMode.TASK);
    querySelector('#input-lineitem-mode').onClick.listen((_) => INPUT_MODE = InputMode.LINEITEM);
}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('ubr-autocomplete', AutoComplete);
    document.registerElement('ubr-job', JobElement);
    document.registerElement('ubr-taskgroup', TaskGroupElement);
    document.registerElement('ubr-task', TaskElement);
    document.registerElement('ubr-taskinstance', TaskInstanceElement);
    document.registerElement('ubr-lineitem', LineItemElement);
    setup_input_mode_buttons();
}
