import 'dart:html';
import 'dart:convert';

socket() {
    var protocol = (window.location.protocol == 'https:') ? 'wss:' : 'ws:';
    return new WebSocket("${protocol}//${window.location.host}/notes");
}

main() {
    BodyElement body = querySelector('body');
    TableSectionElement notes = querySelector('#notes');
    socket().onMessage.listen((event) {
        Map data = JSON.decode(event.data);
        TableRowElement tr = notes.addRow();
        TableCellElement td = tr.addCell();
        if (data.containsKey('project-id')) {
            td.append(new AnchorElement()
                ..href=data['project-url']
                ..text="#${data['project-id']}"
            );
        }
        td.appendHtml(" ${data['user']}<br><span>${data['created']}</span>", treeSanitizer: NodeTreeSanitizer.trusted);
        tr.addCell().appendHtml(data['html'], treeSanitizer: NodeTreeSanitizer.trusted);
        notes.children.reversed.skip(30).toList().forEach((e)=>e.remove());
        body.scrollTop = body.scrollHeight;
    });
}