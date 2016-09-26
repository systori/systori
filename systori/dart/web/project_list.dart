import 'dart:html';
import 'package:collection';
import 'dart:async';
import 'dart:developer';

void main() {
  List<Element> rows = querySelectorAll('.project_row');
//  for (var row in rows) {
//    int id = row.dataset['project-id'];
//    debugger();
//    row.children[0].text = "hallo $id";
//  }
  var sorted = new Collection(rows)
    .orderBy((row) => row.length)
    .thenBy((row) => row);
}