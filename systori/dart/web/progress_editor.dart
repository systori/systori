import 'dart:html';
import 'package:intl/intl.dart';


class ProgressTable extends TableElement {

    CheckboxInputElement complete_checkbox;
    SelectElement worker_select;

    ElementList<ProgressRow> get rows =>
            this.querySelectorAll(':scope>tbody>tr[is="progress-row"]');

    ProgressTable.created() : super.created(); attached() {
        complete_checkbox = this.querySelector(':scope>thead input[type="checkbox"]');
        complete_checkbox.onChange.listen(set_complete);
        worker_select = this.querySelector(':scope>thead select[name="worker"]');
        worker_select.onChange.listen(set_worker);
    }

    set_worker([Event e]) =>
        rows.forEach((row) => row.set_worker(worker_select.value));

    set_complete([Event e]) {
        complete_checkbox.setAttribute('disabled', 'true');
        rows.forEach((row) => row.set_complete(true));
    }

}

class ProgressRow extends TableRowElement {

    SelectElement worker_select;
    InputElement completed_input;
    CheckboxInputElement complete_checkbox;

    ProgressRow.created() : super.created(); attached() {
        worker_select = this.querySelector(':scope select');
        completed_input = this.querySelector(':scope .completed-input');
        complete_checkbox = this.querySelector(':scope input[type="checkbox"]');
        complete_checkbox.onChange.listen((e) => set_complete(complete_checkbox.checked));
    }

    set_worker(var worker) {
        worker_select.value = worker;
    }

    set_complete(bool toggle) {
        if (toggle) {
            complete_checkbox.checked = true;
            completed_input.value = completed_input.dataset['full-qty'];
        }
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('progress-table', ProgressTable, extendsTag:'table');
    document.registerElement('progress-row', ProgressRow, extendsTag:'tr');
}
