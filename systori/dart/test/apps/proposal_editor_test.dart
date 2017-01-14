import 'dart:html';
import 'package:test/test.dart';
import '../../web/proposal_editor.dart';

void main() {
    group('Proposal Editor', () {
        test('ProposalTable', () {
            ProposalTable table = document.querySelector('table[is="proposal-table"]');
            table.recalculate();
        });
    });
}
