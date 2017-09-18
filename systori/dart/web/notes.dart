import 'dart:html';
import 'dart:convert';
import 'dart:async';
import 'dart:io' as io;
import 'package:intl/intl.dart';


var CSRFToken;
var note;
var note_id;
var note_url = window.location.origin+"/api/note/";
var editarea = """
    <td>
    <textarea class="note-textarea">${note["text"]}</textarea>
    <note-save-button data-note-id='$note_id' class="btn btn-xs btn-primary">Save</note-save-button>
    </td>
    """;

class NoteBtnGroup extends HtmlElement {
    static final tag = 'note-btn-group';

    NoteBtnGroup.created() : super.created() {
        var created = DateTime.parse(this.closest("tr").dataset['noteCreated']);
        Duration age = created.difference(new DateTime.now());
        var isOwner = this.closest("tr").dataset['workerPk'] == document.querySelector("#currentUser").dataset['workerPk'];
        if (age.inHours > -2 && isOwner)
            this.classes.remove('hidden');
    }
}

class NoteDeleteButton extends HtmlElement {
    static final tag = 'note-delete-button';

    NoteDeleteButton.created() : super.created() {
        this.onClick.listen((_) {
            note_id = int.parse(this.closest("tr").dataset['note-id']);
            noteDelete(note_id);
        });
    }

    void noteDelete(note_id) {
        String url = note_url + note_id.toString();
        HttpRequest.request(url, method: 'delete', requestHeaders: {"X-CSRFToken": CSRFToken}).then(removeFromDom);
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

    NoteEditButton.created() : super.created() {
        this.onClick.listen((_) {
            note_id = int.parse(this.closest("tr").dataset['note-id']);
            noteEdit(note_id);
        });
    }

    void noteEdit(note_id) {
        String url = note_url + note_id.toString();
        HttpRequest.request(url,
                method: 'get').then(createEditArea);
    }

    void createEditArea(var response) {
        if (response.status == 200) {
            note = JSON.decode(response.response);
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
    var note_id;

    NoteSaveButton.created() : super.created() {
        this.onClick.listen((_) {
            note_id = int.parse(this.closest("tr").dataset['note-id']);
            noteSave(note_id);
        });
    }

    void noteSave(note_id) {
        String url = note_url + note_id.toString();
        TextAreaElement textarea = this.parent.querySelector("textarea");
        note["text"] = textarea.value;
        HttpRequest.request(url,
                method: 'put',
                sendData: JSON.encode(note),
                requestHeaders: {
                    "X-CSRFToken": CSRFToken,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                    })
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
    document.registerElement('note-btn-group', NoteBtnGroup);
}