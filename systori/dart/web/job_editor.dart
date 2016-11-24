import 'package:systori/editor.dart';

main() {
    changeManager = new ChangeManager(new Repository());
    registerElements();
    changeManager.startAutoSync();
}
