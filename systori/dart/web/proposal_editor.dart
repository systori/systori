import 'dart:html';
import 'package:intl/intl.dart';
import 'package:systori/inputs.dart';
import 'package:systori/decimal.dart';


class ProposalTable extends TableElement {

    AmountViewCell estimate_total_cell;

    double tax_rate;

    ElementList<ProposalRow> get rows =>
            this.querySelectorAll(":scope tr.proposal-row.is-attached");

    ProposalTable.created() : super.created(); attached() {
        TableRowElement totals = this.querySelector(":scope tr.proposal-table-totals");
        this.estimate_total_cell = totals.querySelector(":scope>.job-estimate");
        tax_rate = double.parse(this.dataset['tax-rate']);
    }

    recalculate() {
        var estimate_total = new Amount.from(0, 0, tax_rate);
        for (var row in rows) {
            estimate_total += row.estimate_cell.amount;
        }
        estimate_total_cell.update(estimate_total);
    }
}


class ProposalRow extends TableRowElement {

    ProposalTable table;

    CheckboxInputElement is_attached_input;

    AmountViewCell estimate_cell;

    bool get is_attached => is_attached_input.checked;

    ProposalRow.created() : super.created(); attached() {
        table = parent.parent;
        is_attached_input = this.querySelector(':scope>.job-is-attached>input');
        is_attached_input.onChange.listen(toggle);
        estimate_cell = this.querySelector(":scope>.job-estimate");
    }

    toggle([Event e]) {
        if (is_attached) {
            classes.add('is-attached');
        } else {
            classes.remove('is-attached');
        }
        table.recalculate();
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    registerAmountElements();
    document.registerElement('proposal-table', ProposalTable, extendsTag:'table');
    document.registerElement('proposal-row', ProposalRow, extendsTag:'tr');
}
