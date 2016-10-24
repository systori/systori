import 'dart:html';
import 'dart:async';
import 'package:intl/intl.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';
import 'package:systori/orderable.dart';
import 'package:systori/inputs.dart';


abstract class Model extends HtmlElement {

    int get pk => int.parse(dataset['pk']);
    int get code => int.parse(dataset['code']);

    List<DivElement> inputs = [];

    Model.created() : super.created();

    HtmlElement getView(String field) =>
        this.querySelector(":scope>.editor .${field}");

    HtmlElement getInput(String field) {
        var div = getView(field);
        inputs.add(div);
        return div;
    }

}


class Job extends Model {
    String get zfill => dataset['zfill'];
    int get levels => int.parse(dataset['levels']);
    Job.created(): super.created();
}


class Group extends Model {
    Group.created(): super.created();
}


class Task extends Model {

    DivElement price_view;
    String get price => price_view.text;
    set price(String _price) => price_view.text = _price;

    DivElement total_view;
    String get total => total_view.text;
    set total(String _total) => total_view.text = _total;

    Task.created(): super.created() {
        price_view = getView("price");
        total_view = getView("total");
        this.on['calculate'].listen((_) => calculate());
    }

    calculate() {
        price = sumChildren().money;
    }

    Decimal sumChildren() {
        var items = this.querySelectorAll('sys-lineitem').map((e) => e.total.value);
        return items.fold(new Decimal(), (a, b) => a + b);
    }

}


class LineItemCell extends HighlightableInput with Cell {

    String get equation => dataset['equation'];
    set equation(String equation) => dataset['equation'] = equation;

    String get resolved => dataset['resolved'];
    set resolved(String equation) => dataset['resolved'] = equation;

    List<StreamSubscription<Event>> subscriptions = [];

    LineItemCell.created(): super.created() {
        value = new Decimal.parse(text);
        if (isContentEditable) enableEditing();
    }

    enableEditing() {
        contentEditable = "true";
        subscriptions = [
            onBlur.listen(handleBlur),
            onFocus.listen(handleFocus),
            onInput.listen(handleInput),
        ];
    }

    disableEditing() {
        contentEditable = "false";
        subscriptions.forEach((s)=>s.cancel());
        subscriptions = [];
    }

    handleFocus(FocusEvent event) {
        if (equation != null)
            text = equation;
        window.getSelection().selectAllChildren(event.target);
        dispatchCalculate();
    }

    handleInput([_]) {
        equation = text.trim();
        dispatchCalculate();
    }

    handleBlur([_]) {
        text = value.money;
    }

    dispatchCalculate([_]) =>
        dispatchEvent(new CustomEvent('calculate', detail: this));

    static final List<String> COLORS = [
        '187,168,146', '238,114,95', '250,185,75', '0,108,124', '0,161,154', '183,219,193'
    ];

    onCalculationFinished() {

        if (document.activeElement != this) {
            text = value.money;
            return;
        }

        if (isEquation) {
            if (resolved != null && resolved.trim() != value.number)
                dataset['preview'] = "${resolved} = ${value.money}";
            else
                dataset['preview'] = value.money;
        } else return;

        if (ranges == null) return;
        highlight(ranges.map((r) =>
            new Highlight(r.srcStart, r.srcEnd, COLORS[r.result.group%COLORS.length]))
        );
    }

}


class LineItem extends Model with Orderable, Row {

    DivElement name;
    DivElement unit;
    bool get hasPercent => unit.text.contains('%');

    LineItemCell qty;
    LineItemCell price;
    LineItemCell total;

    LineItem.created(): super.created() {
        name = getInput("name");
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
    }

    onCalculationFinished() {
        List<LineItemCell> cols = columns, blank = [], other = [];
        cols.forEach((c)=> c.isBlank ? blank.add(c) : other.add(c));
        if (blank.length == 1) {
            if (blank[0].isContentEditable)  blank[0].disableEditing();
            if (!other[0].isContentEditable) other[0].enableEditing();
            if (!other[1].isContentEditable) other[1].enableEditing();
        } else {
            if (!cols[0].isContentEditable) cols[0].enableEditing();
            if (!cols[1].isContentEditable) cols[1].enableEditing();
            if (!cols[2].isContentEditable) cols[2].enableEditing();
        }
    }

}


class LineItemContainer extends HtmlElement with OrderableContainer, Spreadsheet {

    List get rows => this.querySelectorAll(':scope>sys-lineitem');

    LineItemContainer.created(): super.created() {
        on['calculate'].listen((CustomEvent e) => calculate(e.detail as Cell));
        addEventListener('blur', clearHighlighting, true);
    }

    onOrderingChanged(LineItem orderable) =>
        dispatchEvent(new CustomEvent('calculate', detail: orderable.getCell(0)));

    onCalculationFinished(Cell changedCell) {

        if (changedCell.ranges == null) return;

        var matrix = new List.generate(rows.length, (i)=>[0,0,0]);

        for (var range in changedCell.ranges) {
            for (int rowIdx = 0; rowIdx < matrix.length; rowIdx++) {
                if (range.result.isHit(rowIdx)) {
                    var colIdx = range.column != null
                            ? range.column
                            : changedCell.column;
                    if (matrix[rowIdx][colIdx] != 0) {
                        matrix[rowIdx][colIdx] = -1;
                    } else {
                        matrix[rowIdx][colIdx] = range.result.group;
                    }
                }
            }
        }

        print(matrix);

        for (int rowIdx = 0; rowIdx < matrix.length; rowIdx++) {
            var row = rows[rowIdx];
            for (int colIdx = 0; colIdx < 3; colIdx++) {
                var col = row.getCell(colIdx) as LineItemCell;
                var group = matrix[rowIdx][colIdx];
                switch(group) {
                    case -1: col.style.background = '#D41351'; break;
                    case 0: col.style.background = null; break;
                    default:
                        col.style.background = 'rgba(${LineItemCell.COLORS[group%LineItemCell.COLORS.length]},0.2)';
                }
            }
        }
    }

    clearHighlighting([_]) {
        for (LineItem row in rows) {
            row.qty.style.background = null;
            row.price.style.background = null;
            row.total.style.background = null;
        }
    }

}


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('sys-job', Job);
    document.registerElement('sys-group', Group);
    document.registerElement('sys-task', Task);
    document.registerElement('sys-lineitem-cell', LineItemCell);
    document.registerElement('sys-lineitem-container', LineItemContainer);
    document.registerElement('sys-lineitem', LineItem);
}
