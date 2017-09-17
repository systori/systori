import 'dart:html';
import 'dart:async';
import 'dart:io' as io;
import 'package:intl/intl.dart';


var CSRFToken;
var rawNote;
var note_id;
var editarea = """
    <td>
    <textarea class="note-textarea">$rawNote</textarea>
    <note-save-button data-note-id='$note_id' class="btn btn-xs btn-primary">Save</note-save-button>
    </td>
    """;

class NoteDeleteButton extends HtmlElement {
    static final tag = 'note-delete-button';
    var note_url = window.location.origin+"/api/note/";
    var note_id;

    NoteDeleteButton.created() : super.created() {
        this.checkAge();
        this.onClick.listen((_) {
            note_id = int.parse(this.dataset['note-id']);
            noteDelete(note_id);
        });
    }

    void noteDelete(note_id) {
        String url = note_url + note_id.toString() + "/delete";
        HttpRequest.request(url, method: 'delete', requestHeaders: {"X-CSRFToken": CSRFToken}).then(removeFromDom);
    }

    void checkAge() {
        var created = DateTime.parse(this.dataset['noteCreated']);
        Duration age = created.difference(new DateTime.now());
        if (age.inHours > -2)
            this.classes.remove('hidden');
    }

    void removeFromDom(var response) {
        if (response.status == 204) {
            document.querySelector("tr[data-note-id='$note_id']").remove();
        } else {
            print('false');
        }
    }
}


class NoteEditButton extends HtmlElement {
    static final tag = 'note-edit-button';
    var note_url = window.location.origin+"/api/note/";

    NoteEditButton.created() : super.created() {
        this.checkAge();
        this.onClick.listen((_) {
            note_id = int.parse(this.dataset['note-id']);
            noteEdit(note_id);
        });
    }

    void noteEdit(note_id) {
        String url = note_url + note_id.toString();
        HttpRequest.request(url,
                method: 'get').then(createEditArea);
    }

    void checkAge() {
        var created = DateTime.parse(this.dataset['noteCreated']);
        Duration age = created.difference(new DateTime.now());
        if (age.inHours > -2)
            this.classes.remove('hidden');
    }

    void createEditArea(var response) {
        if (response.status == 200) {
            rawNote = response.response;
            document.querySelectorAll("note-edit-button").forEach((e) {e.classes.add('hidden');});
            document.
                querySelector("tr[data-note-id='$note_id'] td:nth-child(2)").
                setInnerHtml(editarea, treeSanitizer: NodeTreeSanitizer.trusted);
        } else {
            print('false');
        }
    }
}


class NoteSaveButton extends HtmlElement {
    static final tag = 'note-save-button';
    var note_url = window.location.origin+"/api/note/";
    var note_id;

    NoteSaveButton.created() : super.created() {
        print("askjdask");
        this.onClick.listen((_) {
            note_id = int.parse(this.dataset['note-id']);
            noteSave(note_id);
        });
    }

    void noteSave(note_id) {
        String url = note_url + note_id.toString() + "/update";
        TextAreaElement textarea = this.parent.querySelector("textarea");
        HttpRequest.request(url,
                method: 'put',
                sendData: textarea.value,
                requestHeaders: {"X-CSRFToken": CSRFToken})
                .then(reload);
    }

    void reload(var reponse) {
        window.location.reload();
    }
}



void main() {
    CSRFToken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
    document.registerElement('note-delete-button', NoteDeleteButton);
    document.registerElement('note-edit-button', NoteEditButton);
    document.registerElement('note-save-button', NoteSaveButton);
}