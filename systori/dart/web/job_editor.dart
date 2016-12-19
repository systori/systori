import 'package:systori/editor.dart';

main() {
    registerElements();
    repository = new Repository();
    changeManager = new ChangeManager(Job.JOB);
    changeManager.startAutoSync();
}
