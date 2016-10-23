import 'dart:html';
import 'package:test/test.dart';
import '../web/amount_element.dart' show Amount;
import '../web/adjustment_editor.dart';
import '../web/adjustment_editor.dart' as adjustment_editor;

void main() { adjustment_editor.main();

    group("AdjustmentTable", () {

        test("is registered", () {
            AdjustmentTable table = querySelector("table");
            expect(table.rows.length, equals(2));
        });

    });

}
