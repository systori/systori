import 'dart:html';
import 'dart:convert';

main() {
    DivElement notes = querySelector('#notes');
    var protocol = (window.location.protocol == 'https:') ? 'wss:' : 'ws:';
    var ws = new WebSocket("${protocol}//${window.location.host}/notes");
    ws.onMessage.listen((event) {
        Map data = JSON.decode(event.data);
        Element tr = new TableRowElement();
        tr.setInnerHtml("""
        <td>
          <nobr><b>${data['user']}</b></nobr>
          <br>
          <span class="note-created" style="color: grey;">${data['created']}</span>
        </td>
        <td>${data['text']}</td>
        """, treeSanitizer: NodeTreeSanitizer.trusted);
        notes.insertBefore(tr, notes.firstChild);
        notes.children.skip(10).toList().forEach((e)=>e.remove());
    });
}