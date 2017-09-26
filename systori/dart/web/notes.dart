import 'dart:html';
import 'dart:convert';


String CSRFToken;
String translated_save;
String note_url = window.location.origin+"/api/note/";


class NoteDeleteButton extends ButtonElement {
    int note_pk;

    NoteDeleteButton.created() : super.created();

    void noteDelete(note_pk) {
        String url = note_url + note_pk.toString();
        HttpRequest.request(url, method: 'delete', requestHeaders: {"X-CSRFToken": CSRFToken}).then(removeFromDom);
    }

    void removeFromDom(var response) {
        if (response.status == 204) {
            document.querySelector("tr[data-note-pk='$note_pk']").remove();
        } else {
            print('false');
        }
    }
}


class NoteEditButton extends ButtonElement {
    Map note;
    int get pk => int.parse(this.closest("tr").dataset['pk']);
    SpanElement get note_span => this.parent.parent.querySelector("span");
    TextAreaElement get textarea => this.parent.parent.querySelector("textarea");
    DivElement get btngrp => this.parent;
    ButtonElement get save_btn => this.parent.parent.querySelector('#note-save-button');

    NoteEditButton.created() : super.created();

    @override
    attached() {
        this.onClick.listen((_) {
            noteEdit();
        });
    }

    void noteEdit() {
        [note_span, textarea, btngrp, save_btn].forEach((el) {
            el.classes.toggle("hidden");
        });
    }
}


class NoteSaveButton extends ButtonElement {

    int get pk => int.parse(this.closest("tr").dataset['pk']);
    NoteSaveButton.created(): super.created();

    @override
    attached() {
        this.onClick.listen((_) {
            noteSave(this, pk);
        });
//        this.parent.querySelector("textarea").addEventListener("keypress", (dynamic e) {
//            if (e.shiftKey && (e.keyCode == 13)) {
//                e.preventDefault();
//                noteSave(this, pk);
//            }
//        });
    }

    void noteSave(NoteSaveButton instance, int pk) {
        String url = note_url + pk.toString();
        TextAreaElement textarea = this.parent.querySelector("textarea");
        HttpRequest.request(url,
                method: 'put',
                sendData: JSON.encode({'text':textarea.value}),
                requestHeaders: {
                    "X-CSRFToken": CSRFToken,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                    }).then((_) => HttpRequest.request(url, method: 'get').then((response) => noteUpdate(instance, response)));
    }

    void noteUpdate(NoteSaveButton instance, response) {
        if (response.status == 200) {
            var data = JSON.decode(response.responseText);
        }
    }
}

class NoteTableRow extends TableRowElement {
    int get pk => int.parse(dataset['pk']);
    set pk (int pk) {
        dataset['pk'] = pk.toString();
    }
    int get worker_pk => int.parse(dataset['workerPk']);
    int get current_worker => int.parse(document.querySelector("#currentWorker").dataset['pk']);
    DateTime get note_created => DateTime.parse(dataset['noteCreated']);

    NoteTableRow.created() : super.created(){
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#note-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
        Duration age = note_created.difference(new DateTime.now());
        bool is_owner = worker_pk == current_worker;
        if (age.inHours > -2 && is_owner)
            this.querySelector('.btn-group').classes.toggle('hidden');
    }
}

class NoteTextArea extends TextAreaElement {
    NoteTextArea.created(): super.created(){
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#note-textarea-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
    }

}


void main() {
    CSRFToken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
    translated_save = querySelector('#translated_save').text;
    document.registerElement('note-delete-button', NoteDeleteButton, extendsTag: 'button');
    document.registerElement('note-edit-button', NoteEditButton, extendsTag: 'button');
    document.registerElement('note-save-button', NoteSaveButton, extendsTag: 'button');
    document.registerElement('note-tr', NoteTableRow, extendsTag: 'tr');
    HtmlElement notes_container = document.querySelector(".notes-table-responsive");
    notes_container.scrollTop = notes_container.scrollHeight - notes_container.clientHeight;
}