@TestOn('browser')
import 'dart:html';
import 'package:test/test.dart';
import '../../web/refund_editor.dart';
import '../../web/refund_editor.dart' as refund_editor;

void main() { refund_editor.main();
    group('Refund Editor', () {
        test('RefundTable', () {
            RefundTable table = document.querySelector('[is="refund-table"]');
            table.recalculate();
        });
    });
}
