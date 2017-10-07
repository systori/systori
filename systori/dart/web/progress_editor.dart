import 'dart:html';
import 'package:intl/intl.dart';
import 'package:systori/numbers.dart';


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
        for (var row in rows) {
            if (row.complete < row.qty) {
                row.set_complete(true);
            }
        }
    }

    reset_complete() =>
        complete_checkbox.checked = rows.every((p) => p.complete_checkbox.checked);

}

class ProgressRow extends TableRowElement {

    SelectElement worker_select;
    InputElement complete_input;
    CheckboxInputElement complete_checkbox;
    ButtonElement reset_button;

    Decimal get complete => new Decimal.parse(complete_input.value);
    Decimal get original => new Decimal.parse(complete_input.dataset['original']);
    Decimal get qty => new Decimal.parse(complete_input.dataset['qty']);

    ProgressRow.created() : super.created(); attached() {
        complete_checkbox = this.querySelector(':scope input[type="checkbox"]');
        complete_checkbox.onChange.listen((e) => set_complete(complete_checkbox.checked));
        complete_input = this.querySelector(':scope input.complete');
        complete_input.onKeyUp.listen(update_complete_state);
        worker_select = this.querySelector(':scope select');
        reset_button = this.querySelector(':scope button');
        reset_button.onClick.listen(reset_state);
    }

    set_worker(var worker) {
        worker_select.value = worker;
    }

    set_complete(bool toggle) {
        if (toggle) {
            complete_checkbox.checked = toggle;
            complete_input.value = complete_input.dataset['qty'];
            update_complete_state();
        }
    }

    update_complete_state([_]) {
        if (complete >= qty) {
            complete_checkbox.checked = true;
            complete_checkbox.setAttribute('disabled', null);
        } else {
            complete_checkbox.checked = false;
            complete_checkbox.attributes.remove('disabled');
        }
        if (complete != original) {
            reset_button.style.visibility = 'visible';
        } else {
            reset_button.style.visibility = 'hidden';
        }
        (parent.parent as ProgressTable).reset_complete();
    }

    reset_state([_]) {
        complete_input.value = complete_input.dataset['original'];
        update_complete_state();
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('progress-table', ProgressTable, extendsTag:'table');
    document.registerElement('progress-row', ProgressRow, extendsTag:'tr');
}
