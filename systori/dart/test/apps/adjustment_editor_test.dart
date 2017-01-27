@TestOn('browser')
import 'dart:html';
import 'dart:async';
import 'package:test/test.dart';
import '../../web/adjustment_editor.dart';
import '../../web/adjustment_editor.dart' as adjustment_editor;
import '../scaffolding.dart';


void main() { adjustment_editor.main();

    AdjustmentTable table;
    Scaffolding scaffold = new Scaffolding(querySelector('[is="adjustment-table"]').parent);

    setUp(() {
        scaffold.reset();
        table = querySelector('[is="adjustment-table"]');
    });

    group("AdjustmentTable", () {

        test("paid cell clicked", () async {

            var row = table.rows[0];

            expect(row.paid_cell.classes, isNot(contains('selected')));
            expect(row.invoiced_cell.classes, contains('selected'));
            expect(row.progress_cell.classes, isNot(contains('selected')));
            expect(row.adjustment_cell.amount.gross.decimal, 0);
            expect(row.corrected_cell.amount.gross.decimal, 480);

            row.column_clicked(row.paid_cell);

            await new Future.value(); // wait for amount change event to propagate

            expect(row.paid_cell.classes, contains('selected'));
            expect(row.invoiced_cell.classes, isNot(contains('selected')));
            expect(row.progress_cell.classes, contains('selected'));
            expect(row.adjustment_cell.amount.gross.decimal, -480);
            expect(row.corrected_cell.amount.gross.decimal, 0);
        });

    });

}
