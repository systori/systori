@TestOn('browser')
import 'dart:html';
import 'package:test/test.dart';
import '../../web/proposal_editor.dart';
import '../../web/proposal_editor.dart' as proposal_editor;

void main() { proposal_editor.main();
    group('Proposal Editor', () {
        test('ProposalTable', () {
            ProposalTable table = document.querySelector('[is="proposal-table"]');
            table.recalculate();
        });
    });
}
