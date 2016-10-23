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

    String get equation => dataset['equation'].isEmpty?null:dataset['equation'];
    set equation(String equation) => dataset['equation'] = equation;

    String get resolved => dataset['resolved'];
    set resolved(String equation) => dataset['resolved'] = equation;

    StreamSubscription<Event> inputSubscription;
    StreamSubscription<Event> focusSubscription;

    LineItemCell.created(): super.created() {
        value = new Decimal.parse(text);
        focusSubscription = onFocus.listen(handleFocus);
        inputSubscription = onInput.listen(handleInput);
        onBlur.listen(handleBlur);
    }

    setText(String txt) {
        inputSubscription.pause();
        focusSubscription.pause();
        text = txt;
        inputSubscription.resume();
        focusSubscription.resume();
    }

    handleFocus(FocusEvent event) {
        print('focus triggered');
        /* This timer solves an annoying situation when user clicks
         * on an input field and two events are fired:
         *   1) onFocus is fired first and the text is selected. So far good.
         *   2) Immediately after onFocus, the onClick event is fired. But the onClick event
         *      default behavior is to place a carret somewhere in the text. This causes the
         *      selection we made in onFocus to be un-selected. :-(
         * The solution is to set a timer that will delay selecting text
         * until after onClick is called. It's a hack but it works.
         */
        //new Timer(new Duration(milliseconds: 1), () {
            if (equation != null)
                setText(equation);
       //     window.getSelection().selectAllChildren(event.target);
            dispatchCalculate();
        //});
    }

    handleInput([_]) {
        equation = text;
        dispatchCalculate();
    }

    handleBlur([_]) {
        setText(value.money);
    }

    dispatchCalculate([_]) =>
        dispatchEvent(new CustomEvent('calculate', detail: this));

    static final List<String> COLORS = [
        '187,168,146', '238,114,95', '250,185,75', '0,108,124', '0,161,154', '183,219,193'
    ];

    onCalculationFinished() {

        if (document.activeElement != this) {
            setText(value.money);
            return;
        }

        if (hasEquation) {
            if (resolved != value.number)
                dataset['preview'] = "${resolved} = ${value.money}";
            else
                dataset['preview'] = value.money;
        } else return;

        inputSubscription.pause();
        focusSubscription.pause();
        //highlight(ranges.map((r) =>
        //    new Highlight(r.srcStart, r.srcEnd, COLORS[r.result.id%COLORS.length]))
        //);
        inputSubscription.resume();
        focusSubscription.resume();

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
    document.registerElement('sys-lineitem-container', LineItemContainer);
    document.registerElement('sys-lineitem-cell', LineItemCell);
    document.registerElement('sys-lineitem', LineItem);
}
