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


class TaskCell extends HtmlElement with Cell {

    String get equation => dataset['equation'];
    set equation(String equation) => dataset['equation'] = equation;

    String get resolved => dataset['resolved'];
    set resolved(String equation) => dataset['resolved'] = equation;

    List<StreamSubscription<Event>> subscriptions = [];

    TaskCell.created(): super.created() {
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

    onCalculationFinished() {
        super.onCalculationFinished();

        if (document.activeElement != this) {
            text = value.money;
            return;
        }

        if (isEquation) {
            if (resolved != null && resolved.trim() != value.number)
                dataset['preview'] = "${resolved} = ${value.money}";
            else
                dataset['preview'] = value.money;
        }

    }

}



class Task extends Model with Row {

    DivElement name;
    DivElement unit;
    TaskCell qty;
    TaskCell price;
    TaskCell total;
    DivElement diffRow;
    DivElement diffCell;

    LineItemSheet sheet;

    Task.created(): super.created() {
        name = getInput("name");
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        diffRow = this.querySelector(":scope> div.price-difference");
        diffCell = diffRow.querySelector(":scope> .total");
        sheet = this.querySelector(":scope > sys-lineitem-sheet");
        this.on['calculate'].listen((_) {
            if (sheet.hasNeverBeenCalculated)
                sheet.calculate(qty);
            calculate(sheet, 0, true);
        });
    }

    solve() {

        if (qty.isNotBlank && total.isBlank) {
            setDiffCell(new Decimal(0));
            total.value = qty.value * price.value;
        } else
        if (qty.isNotBlank && total.isNotBlank) {
            var task_price = total.value / qty.value;
            setDiffCell(task_price  - price.value);
            price.value = total.value / qty.value;
        } else
        if (qty.isBlank && total.isNotBlank) {
            setDiffCell(new Decimal(0));
            qty.value = total.value / price.value;
        }
    }

    setDiffCell(Decimal diff) {
        if (diff.isZero) {
            diffRow.style.visibility = 'hidden';
            diffCell.text = '0';
        } else {
            diffRow.style.visibility = 'visible';
            diffCell.text = diff.money;
        }
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
        super.onCalculationFinished();

        if (document.activeElement != this) {
            text = value.money;
            return;
        }

        if (isEquation) {
            if (resolved != null && resolved.trim() != value.number)
                dataset['preview'] = "${resolved} = ${value.money}";
            else
                dataset['preview'] = value.money;
        } else if (isBlank && value.isNonzero) {
            dataset['preview'] = value.money;
        } else {
            dataset['preview'] = "";
        }

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
        super.onCalculationFinished();
        if (qty.isNotBlank && price.isNotBlank && total.isNotBlank) {
            [qty,price,total].forEach((Element e)=>e.style.color = 'red');
        } else {
            [qty,price,total].forEach((Element e)=>e.style.color = null);
        }
    }
}


class LineItemSheet extends HtmlElement with OrderableContainer, Spreadsheet {

    List get rows => this.querySelectorAll(':scope>sys-lineitem');

    LineItemSheet.created(): super.created() {
        on['calculate'].listen((CustomEvent e) => calculate(e.detail as Cell));
        addEventListener('blur', clearHighlighting, true);
    }

    onOrderingChanged(LineItem orderable) =>
        dispatchEvent(new CustomEvent('calculate', detail: orderable.getCell(0)));

    onCalculationFinished(Cell changedCell) {
        super.onCalculationFinished(changedCell);

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
    document.registerElement('sys-lineitem-cell', LineItemCell);
    document.registerElement('sys-lineitem', LineItem);
    document.registerElement('sys-lineitem-sheet', LineItemSheet);
    document.registerElement('sys-task-cell', TaskCell);
    document.registerElement('sys-task', Task);
    document.registerElement('sys-job', Job);
    document.registerElement('sys-group', Group);
}
