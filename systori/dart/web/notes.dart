import 'dart:html';
import 'dart:convert';


String CSRFToken;
String translated_save;
String note_url = window.location.origin+"/api/note/";


void checkBtnGroupDisplay({bool forceHide}) {

    document.querySelectorAll('note-btn-group').forEach((e) {
        DateTime created = DateTime.parse(e.closest("tr").dataset['noteCreated']);
        Duration age = created.difference(new DateTime.now());
        bool isOwner = e.closest("tr").dataset['workerPk'] == document.querySelector("#currentUser").dataset['workerPk'];

        if (age.inHours > -2 && isOwner)
            e.classes.toggle('hidden');
        if (forceHide)
            e.classes.toggle('hidden', true); // bool shouldAdd
    });
}


class NoteDeleteButton extends HtmlElement {
    int note_pk;

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
    factory NoteDeleteButton() {
        NoteDeleteButton btn = new Element.tag('note-delete-button');
        btn.classes.addAll(['btn', 'btn-sm', 'btn-danger']);
        btn.innerHtml = '<span class="glyphicon glyphicon-trash"></span>';
        return btn;
    }
}


class NoteEditButton extends HtmlElement {
    int note_pk;
    Map note;

    String noteCell(Map data) {
        TableCellElement td = new TableCellElement();
        TextAreaElement ta = new TextAreaElement()
            ..classes.add('note-textarea')
            ..innerHtml = data['text'];
        NoteSaveButton saveBtn = new NoteSaveButton(data['pk']);
        td.children.add(ta);
        td.children.add(saveBtn);

        return td.outerHtml;
    }

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
                setInnerHtml(noteCell(note), treeSanitizer: NodeTreeSanitizer.trusted);
        } else {
            print('Error: Note edit area couldn\'t be created.');
        }
    }

    factory NoteEditButton() {
        NoteEditButton btn = new Element.tag('note-edit-button');
        btn.classes.addAll(['btn', 'btn-sm', 'btn-default']);
        btn.innerHtml = '<span class="glyphicon glyphicon-edit"></span>';
        return btn;
    }
}


class NoteSaveButton extends HtmlElement {
    int note_pk;

    NoteSaveButton.created(): super.created();

    @override
    attached() {
        this.onClick.listen((_) {
            note_pk = int.parse(this.closest("tr").dataset['notePk']);
            noteSave(this, note_pk);
        });
        this.parent.querySelector("textarea").addEventListener("keypress", (dynamic e) {
            note_pk = int.parse(this.closest("tr").dataset['notePk']);
            if (e.shiftKey && (e.keyCode == 13)) {
                e.preventDefault();
                noteSave(this, note_pk);
            }
        });
    }

    factory NoteSaveButton(note_pk) {
        NoteSaveButton btn = new Element.tag('note-save-button');
        btn.classes.addAll(['btn', 'btn-xs', 'btn-primary']);
        btn.dataset.addAll({'notePk':note_pk.toString()});
        btn.text = translated_save;
        return btn;
    }

    void noteSave(NoteSaveButton instance, int note_pk) {
        String url = note_url + note_pk.toString();
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
            TableCellElement td = instance.closest("td");
            Element btngrp = new Element.tag("note-btn-group")
                ..classes.addAll(['btn-group', 'btn-group-sm', 'btn-group-note', 'hidden'])
                ..attributes.addAll({'role': 'group'});
            NoteEditButton editBtn = new NoteEditButton();
            NoteDeleteButton deleteBtn = new NoteDeleteButton();
            btngrp.children.addAll([editBtn, deleteBtn]);
            td.setInnerHtml(data['html']+btngrp.outerHtml,
                    treeSanitizer: NodeTreeSanitizer.trusted);
            checkBtnGroupDisplay();
        }
    }
}


void main() {
    CSRFToken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
    translated_save = querySelector('#translated_save').text;
    document.registerElement('note-delete-button', NoteDeleteButton);
    document.registerElement('note-edit-button', NoteEditButton);
    document.registerElement('note-save-button', NoteSaveButton);

    checkBtnGroupDisplay();
    HtmlElement notes_container = document.querySelector(".notes-table-responsive");
    notes_container.scrollTop = notes_container.scrollHeight - notes_container.clientHeight;
}