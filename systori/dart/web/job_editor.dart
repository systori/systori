import 'package:systori/editor.dart';

main() {
    registerElements();
    changeManager = new ChangeManager(Job.JOB, new Repository());
    changeManager.startAutoSync();
}
