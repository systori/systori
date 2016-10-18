import 'dart:html';
import 'package:intl/intl.dart';
import 'package:systori/summing_sheet.dart';
import 'package:systori/orderable_container.dart';
import 'package:systori/common.dart';


abstract class ModelElement extends HtmlElement {

    int get pk => int.parse(dataset['pk']);
    int get code => int.parse(dataset['code']);

    List<DivElement> inputs = [];

    ModelElement.created() : super.created();

    DivElement getView(String field) =>
        this.querySelector(":scope>.editor .${field}");

    DivElement getInput(String field) {
        var div = getView(field);
        inputs.add(div);
        return div;
    }

}


class JobElement extends ModelElement {
    String get zfill => dataset['zfill'];
    int get levels => int.parse(dataset['levels']);
    JobElement.created(): super.created();
}


class GroupElement extends ModelElement {
    GroupElement.created(): super.created();
}


class TaskElement extends ModelElement {

    DivElement price_view;
    String get price => price_view.text;
    set price(String _price) => price_view.text = _price;

    DivElement total_view;
    String get total => total_view.text;
    set total(String _total) => total_view.text = _total;

    TaskElement.created(): super.created() {
        price_view = getView("price");
        total_view = getView("total");
        this.on['calculate'].listen((_) => calculate());
    }
    calculate() {
        price = amount_int_to_string(children_total());
    }
    children_total() {
        var items = this.querySelectorAll('sys-lineitem').map((e) => amount_string_to_int(e.total));
        return items.fold(0, (a, b) => a + b);
    }
}


class LineItemElement extends ModelElement with Orderable, SummingRow {

    DivElement name_input;

    DivElement qty_input;
    String get qty => qty_input.text;

    DivElement unit_input;
    String get unit => unit_input.text;

    DivElement price_input;
    String get price => price_input.text;
    set price(String _price) => price_input.text = _price;
    set isPriceCalculated(bool _calculated) {
        if (_calculated) {
            price_input.contentEditable = 'false';
        } else {
            price_input.contentEditable = 'true';
        }
    }

    DivElement total_view;
    String get total => total_view.text;
    set total(String _total) => total_view.text = _total;

    LineItemElement.created(): super.created() {
        name_input = getInput("name");
        qty_input = getInput("qty");
        unit_input = getInput("unit");
        unit_input.onFocus.listen(askParentToRecalculate);
        unit_input.onBlur.listen(clearHighlighting);
        price_input = getInput("price");
        [qty_input, unit_input, price_input].forEach((var view) =>
            view.onKeyUp.listen((_) =>
                this.dispatchEvent(new CustomEvent('calculate', detail: this))
            )
        );
        total_view = getView("total");
    }

    askParentToRecalculate([_]) {
        (parent as LineItemContainerElement).calculate();
    }

    clearHighlighting([_]) {
        LineItemElement previous = previousElementSibling;
        while (previous != null) {
            previous.total_view.style.backgroundColor = 'white';
            previous = previous.previousElementSibling;
        }
        this.price_input.style.backgroundColor = 'white';
    }

    onCalculationFinished() {
        if (document.activeElement != this.unit_input || !equation.isSum) return;
        clearHighlighting();
        int i = equation.sumX;
        LineItemElement previous = previousElementSibling;
        while (i > 0 && previous != null) {
            previous.total_view.style.backgroundColor = '#FBCEB1';
            previous = previous.previousElementSibling;
            i--;
        }
        this.price_input.style.backgroundColor = '#F88379';
    }

}


class LineItemContainerElement extends HtmlElement with OrderableContainer, SummingSheet {
    get rows => this.querySelectorAll(':scope>sys-lineitem');
    LineItemContainerElement.created(): super.created() {
        this.on['calculate'].listen((_) => calculate());
    }
    onOrderingFinished(Orderable order) =>
        this.dispatchEvent(new CustomEvent('calculate', detail: this));
}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('sys-job', JobElement);
    document.registerElement('sys-group', GroupElement);
    document.registerElement('sys-task', TaskElement);
    document.registerElement('sys-lineitem', LineItemElement);
    document.registerElement('sys-lineitem-container', LineItemContainerElement);
}
