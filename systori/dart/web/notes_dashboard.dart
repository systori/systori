import 'dart:html';
import 'dart:convert';

socket() {
    var protocol = (window.location.protocol == 'https:') ? 'wss:' : 'ws:';
    return new WebSocket("${protocol}//${window.location.host}/notes");
}

void createNote(BodyElement body, TableSectionElement notes, Map data) {
    TableRowElement tr = notes.addRow();
    tr.dataset['notePk'] = data['note-pk'].toString();
    TableCellElement td = tr.addCell();
    if (data.containsKey('project-id')) {
        td.append(new AnchorElement()
            ..href=data['project-url']
            ..text="#${data['project-id']}"
        );
    }
    td.appendHtml(" ${data['user']}<br><span>${data['created']}</span>", treeSanitizer: NodeTreeSanitizer.trusted);
    tr.addCell().appendHtml(data['html'], treeSanitizer: NodeTreeSanitizer.trusted);
//    notes.children.reversed.skip(30).toList().forEach((e)=>e.remove());
    tr.scrollIntoView();
}

void modifyNote(BodyElement body, TableSectionElement notes, Map data, {bool delete}) {
    var note = document.querySelector('tr[data-note-pk="${data['note-pk']}"]');
    note.querySelector('#note_html').setInnerHtml(data['html'], treeSanitizer: NodeTreeSanitizer.trusted);
    if (delete)
        note.remove();
}

main() {
    BodyElement body = querySelector('body');
    TableSectionElement notes = querySelector('#notes');
    socket().onMessage.listen((event) {
        Map data = JSON.decode(event.data);
        var op = data['op'];
        if (op == 'created') {
            createNote(body, notes, data);
        }
        else if (op == 'delete') {
            modifyNote(body, notes, data, delete:true);
        }
        else if (op == 'update') {
            modifyNote(body, notes, data, delete:false);
        }
        else {
            print("error, no known signal came from server.");
        }
    });
    body.scrollTop = body.clientHeight;
}