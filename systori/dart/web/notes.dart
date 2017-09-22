import 'dart:html';
import 'dart:convert';


var CSRFToken;
var note;
var note_pk;
var note_url = window.location.origin+"/api/note/";
var editarea = """
    <td>
    <textarea class="note-textarea">${note["text"]}</textarea>
    <note-save-button data-note-pk='$note_pk' class="btn btn-xs btn-primary">Save</note-save-button>
    </td>
    """;


void checkBtnGroupDisplay({bool forceHide}) {
    document.querySelectorAll('note-btn-group').forEach((e) {
        DateTime created = DateTime.parse(e.closest("tr").dataset['noteCreated']);
        Duration age = created.difference(new DateTime.now());
        bool isOwner = e.closest("tr").dataset['workerPk'] == document.querySelector("#currentUser").dataset['workerPk'];

        if (age.inHours > -2 && isOwner)
            e.classes.toggle('hidden');
        if (forceHide)
           e.classes.add('hidden');
    });
}


class NoteBtnGroup extends HtmlElement {
    static final tag = 'note-btn-group';

    NoteBtnGroup.created() : super.created() {

    }
}


class NoteDeleteButton extends HtmlElement {
    static final tag = 'note-delete-button';

    NoteDeleteButton.created() : super.created() {
        this.onClick.listen((_) {
            note_pk = int.parse(this.closest("tr").dataset['notePk']);
            noteDelete(note_pk);
        });
    }

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


class NoteEditButton extends HtmlElement {
    static final tag = 'note-edit-button';

    NoteEditButton.created() : super.created() {
        this.onClick.listen((_) {
            note_pk = int.parse(this.closest("tr").dataset['notePk']);
            noteEdit(note_pk);
        });
    }

    void noteEdit(note_pk) {
        String url = note_url + note_pk.toString();
        HttpRequest.request(url,
                method: 'get').then(createEditArea);
    }

    void createEditArea(var response) {
        if (response.status == 200) {
            checkBtnGroupDisplay(forceHide: true);
            note = JSON.decode(response.response);
            document.
                querySelector("tr[data-note-pk='$note_pk'] td:nth-child(2)").
                setInnerHtml(editarea, treeSanitizer: NodeTreeSanitizer.trusted);
        } else {
            print('false');
        }
    }
}


class NoteSaveButton extends HtmlElement {
    static final tag = 'note-save-button';
    var note_pk;

    NoteSaveButton.created() : super.created() {
        this.onClick.listen((_) {
            note_pk = int.parse(this.closest("tr").dataset['notePk']);
            noteSave(note_pk);
        });
        this.parent.querySelector("textarea").addEventListener("keypress", (dynamic e) {
            note_pk = int.parse(this.closest("tr").dataset['notePk']);
            if (e.shiftKey && (e.keyCode == 13)) {
                e.preventDefault();
                noteSave(note_pk);
            }
        });
    }

    void noteSave(note_pk) {
        String url = note_url + note_pk.toString();
        TextAreaElement textarea = this.parent.querySelector("textarea");
        note["text"] = textarea.value;
        HttpRequest.request(url,
                method: 'put',
                sendData: JSON.encode(note),
                requestHeaders: {
                    "X-CSRFToken": CSRFToken,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                    }).then((_) => HttpRequest.request(url, method: 'get').then((response) => noteUpdate(response)));
    }

    void noteUpdate(var response) {
        if (response.status == 200) {
            var data = JSON.decode(response.responseText);
            this.closest("td").innerHtml = data['html'];
            print("received");
        }
    }
}


void main() {
    CSRFToken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
    document.registerElement('note-delete-button', NoteDeleteButton);
    document.registerElement('note-edit-button', NoteEditButton);
    document.registerElement('note-save-button', NoteSaveButton);
    document.registerElement('note-btn-group', NoteBtnGroup);

    checkBtnGroupDisplay();
    HtmlElement notes_container = document.querySelector(".notes-table-responsive");
    notes_container.scrollTop = notes_container.scrollHeight - notes_container.clientHeight;
}