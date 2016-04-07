import 'dart:html';
import 'package:test/test.dart';
import '../web/amount_element.dart' show Amount;
import '../web/payment_editor.dart';
import '../web/payment_editor.dart' as payment_editor;

void main() { payment_editor.main();

    group("AdjustmentTable", () {

        test("is registered", () {
            PaymentSplitTable table = querySelector("table");
            expect(table.rows.length, equals(2));
        });

    });

}
