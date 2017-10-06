import 'dart:html';
import 'package:intl/intl.dart';


class ProgressTable extends TableElement {

    SelectElement worker_select;
    CheckboxInputElement complete_checkbox;

    ElementList<ProgressRow> get rows =>
            this.querySelectorAll(':scope>tbody>tr[is="progress-row"]');

    ProgressTable.created() : super.created(); attached() {
        worker_select = this.querySelector(':scope>thead select[name="worker"]');
        worker_select.onChange.listen(set_worker);
        complete_checkbox = this.querySelector(':scope>thead input[type="checkbox"]');
        complete_checkbox.onChange.listen(set_complete);
    }

    set_worker([Event e]) =>
        rows.forEach((row) => row.set_worker(worker_select.value));

    set_complete([Event e]) =>
            rows.forEach((row) => row.set_complete());

}

class ProgressRow extends TableRowElement {

    SelectElement worker_select;
    InputElement completed_input;

    ProgressRow.created() : super.created(); attached() {
        worker_select = this.querySelector(':scope select');
        completed_input = this.querySelector(':scope .completed-input');
    }

    set_worker(var worker) {
        worker_select.value = worker;
    }

    set_complete() {
        completed_input.value = completed_input.dataset['full-qty'];
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('progress-table', ProgressTable, extendsTag:'table');
    document.registerElement('progress-row', ProgressRow, extendsTag:'tr');
}
