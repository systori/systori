import 'dart:html';
import 'package:systori/editor.dart';

main() {
    registerElements();
    repository = new Repository();
    changeManager = new ChangeManager(Job.JOB);
    autocomplete = document.createElement('sys-autocomplete');
    changeManager.startAutoSync();
}
