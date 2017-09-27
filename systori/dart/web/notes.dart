import 'dart:html';
import 'dart:convert';


String CSRFToken;
String translated_save;
String note_url = window.location.origin+"/api/note/";


class NoteTableRow extends TableRowElement {
    int get pk => int.parse(dataset['pk']);
    int get worker_pk => int.parse(dataset['workerPk']);
    int get current_worker => int.parse(document.querySelector("#currentWorker").dataset['pk']);
    DateTime get note_created => DateTime.parse(dataset['noteCreated']);
    ButtonElement edit_button;
    ButtonElement delete_button;
    ButtonElement save_button;
    SpanElement html_container;
    TextAreaElement textarea;

    NoteTableRow.created() : super.created(){
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#note-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
        edit_button = this.querySelector("#note-edit-button");
        delete_button = this.querySelector("#note-delete-button");
        save_button = this.querySelector("#note-save-button");
        html_container = this.querySelector(".html_container");
        textarea = this.querySelector("textarea");
    }

    @override
    attached() {
        Duration age = note_created.difference(new DateTime.now());
        bool is_owner = worker_pk == current_worker;
        if (age.inHours > -2 && is_owner)
            [edit_button, delete_button].forEach((el) {el.classes.toggle("hidden");});
        edit_button.onClick.listen(noteEdit);
        delete_button.onClick.listen(noteDelete);
        save_button.onClick.listen(noteSave);
        textarea.onKeyPress.listen(noteSave);
    }

    toggleDisplay() {
        [html_container, textarea, save_button, edit_button, delete_button]
                .forEach((el) {el.classes.toggle("hidden");});
    }

    noteEdit(MouseEvent e) {
        toggleDisplay();
    }

    noteDelete(MouseEvent e) {
        String url = note_url + pk.toString();
        HttpRequest.request(url, method: 'delete',
                requestHeaders: {"X-CSRFToken": CSRFToken})
                .then((response) {
            if (response.status == 204) {
                this.remove();
            }
            else {print("error while trying to delte note $pk");}
        });
    }

    noteSave(Event e) {
        if (e is MouseEvent || (e is KeyboardEvent && e.keyCode == 13 && e.shiftKey)) {
            HttpRequest.request(note_url + pk.toString(),
                    method: 'put',
                    sendData: JSON.encode({'text': textarea.value}),
                    requestHeaders: {
                        "X-CSRFToken": CSRFToken,
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }).then((_) =>
                    HttpRequest.request(note_url + pk.toString(), method: 'get')
                            .then((response) =>
                            html_container.setInnerHtml(
                                    JSON.decode(response.responseText)['html'],
                                    treeSanitizer: NodeTreeSanitizer.trusted)));
        toggleDisplay();
        }
    }
}


void main() {
    CSRFToken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
    document.registerElement('note-tr', NoteTableRow, extendsTag: 'tr');

    document.querySelector('#note-input').onKeyPress.listen((e) {
       if (e.keyCode == 13 && e.shiftKey) {
           e.preventDefault();
           (document.querySelector('#note-form') as FormElement).submit();
       }
    });

    HtmlElement notes_container = document.querySelector(".notes-table-responsive");

    notes_container.scrollTop = notes_container.scrollHeight - notes_container.clientHeight;
}