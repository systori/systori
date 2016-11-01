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
    set pk(int id) => dataset['pk'] = id.toString();

    int get order => int.parse(dataset['order']);

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


class GAEBHierarchyStructure {
    // See also Python version in apps/project/models.py

    final String structure;
    final List<int> zfill;

    GAEBHierarchyStructure(String structure):
        structure = structure,
        zfill = structure.split('.').map((s)=>s.length).toList();

    String _format(String position, int zfill) => position.padLeft(zfill, '0');
    String format_task(String position) => _format(position, zfill[-1]);
    String format_group(String position, int level) => _format(position, zfill[level]);
    bool has_level(int level) => 0 <= level && level < (zfill.length-1);
}


class Job extends Group {
    static Job JOB;
    GAEBHierarchyStructure structure;
    int level = 0;
    Job.created(): super.created(); attached() {
        structure = new GAEBHierarchyStructure(dataset['structure-format']);
        JOB = this;
    }
}


class Group extends Model {

    Group get parentGroup => parent as Group;
    DivElement code;
    DivElement name;
    DivElement description;

    bool get isEmpty => name.text.isEmpty;
    int get level => (parent as Group).level + 1;

    set order(int position) {
        dataset['order'] = position.toString();
        code.text = "${parentGroup.code.text}.${Job.JOB.structure.format_group(dataset['order'], level)}";
    }

    Group.created(): super.created() {
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#group-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
        code = getView("code");
        name = getInput("name");
        name.onKeyDown.listen(handleKeyboard);
    }

    handleKeyboard(KeyboardEvent e) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (Job.JOB.structure.has_level(level+1)) {
                Group child = this.querySelector(':scope>sys-group') as Group;
                if (child.isEmpty) {
                    child.name.focus();
                } else {
                    Group group = document.createElement('sys-group');
                    insertBefore(group, child);
                    group.generateGroups();
                    updateCode();
                    group.name.focus();
                }
            }
        }
    }

    generateGroups() {
        if (Job.JOB.structure.has_level(level+1)) {
            Group group = document.createElement('sys-group');
            children.add(group);
            group.generateGroups();
        }
    }

    updateCode() {
        enumerate/*<Group>*/(this.querySelectorAll(':scope>sys-group'))
            .forEach((IndexedValue<Group> g) {
            g.value.order = g.index+1;
            g.value.updateCode();
        });
    }

}


abstract class HtmlCell implements HtmlElement, Cell {

    String get canonical => dataset['canonical'];
    set canonical(String canonical) => dataset['canonical'] = canonical;

    String get local => dataset['local'];
    set local(String local) => dataset['local'] = local;

    String get resolved => dataset['resolved'];
    set resolved(String resolved) => dataset['resolved'] = resolved;

    String get preview => dataset['preview'];
    set preview(String preview) => dataset['preview'] = preview;

    List<StreamSubscription<Event>> subscriptions = [];

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

    handleFocus(Event event) {
        if (isCanonicalEquation) {
            dispatchCalculate('focused');
            text = local;
        } else if (isCanonicalBlank) {
            text = "0";
            preview = value.money;
            selectThis();
        } else {
            text = canonical;
            preview = "";
            selectThis();
        }
    }

    handleInput([Event _]) {
        local = text.trim();
        dispatchCalculate('changed');
    }

    handleBlur([Event _]) {
        text = value.money;
    }

    selectThis() {
        new Timer(new Duration(milliseconds: 1), () {
            window.getSelection().selectAllChildren(this);
        });
    }

    dispatchCalculate(String event) =>
        dispatchEvent(new CustomEvent('calculate.$event', detail: this));

    onRowCalculationFinished() {

        if (document.activeElement != this) {
            text = value.money;
            return;
        }

        if (preview != null && preview.startsWith('character ')) return;
        if (isLocalEquation) {
            if (resolved != null && resolved.trim() != value.number)
                preview = "${resolved} = ${value.money}";
            else
                preview = value.money;
        } else if (isLocalBlank && value.isNonzero) {
            preview = value.money;
        }
        print(preview);

    }

}


class TaskCell extends HtmlElement with Cell, HtmlCell {

    TaskCell.created(): super.created() {
        value = new Decimal.parse(text);
        if (isContentEditable) enableEditing();
    }

}



class Task extends Model with Row {

    DivElement name;
    DivElement unit;
    bool get hasPercent => unit.text.contains('%');
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
        on['calculate.focused'].listen((CustomEvent e) => calculate(sheet, 0, e.detail as Cell, focused: true));
        on['calculate.changed'].listen((CustomEvent e) => calculate(sheet, 0, e.detail as Cell, changed: true));
        on['calculate.moved'].listen((CustomEvent e) => calculate(sheet, 0, e.detail as Cell, moved: true));
    }

    onRowCalculationFinished() {

    }

    /*
    solve() {

        if (qty.isCanonicalBlankNotBlank && total.isBlank) {
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
    }*/

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


class LineItemCell extends HighlightableInput with Cell, HtmlCell {

    LineItemCell.created(): super.created() {
        value = new Decimal.parse(text);
        if (isContentEditable) enableEditing();
    }

    static final List<String> COLORS = [
        '187,168,146', '238,114,95', '250,185,75', '0,108,124', '0,161,154', '183,219,193'
    ];

    onRowCalculationFinished() {
        super.onRowCalculationFinished();
        if (document.activeElement != this) return;
        if (resolver.ranges.isEmpty) return;
        new Timer(new Duration(milliseconds: 1), () {
            highlight(resolver.ranges.map((r) =>
                new Highlight(r.srcStart, r.srcEnd, COLORS[r.result.group%COLORS.length]))
            );
        });
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

    onRowCalculationFinished() {
        if (qty.isCanonicalNotBlank && price.isCanonicalNotBlank && total.isCanonicalNotBlank) {
            [qty,price,total].forEach((Element e)=>e.style.color = 'red');
        } else {
            [qty,price,total].forEach((Element e)=>e.style.color = null);
        }
    }
}


class LineItemSheet extends HtmlElement with OrderableContainer, Spreadsheet {

    List<LineItem> get rows => this.querySelectorAll(':scope>sys-lineitem');

    LineItemSheet.created(): super.created() {
        on['calculate.focused'].listen((CustomEvent e) => calculate(e.detail as Cell, focused: true));
        on['calculate.changed'].listen((CustomEvent e) => calculate(e.detail as Cell, changed: true));
        on['calculate.moved'].listen((CustomEvent e) => calculate(e.detail as Cell, moved: true));
        addEventListener('blur', clearHighlighting, true);
    }

    onOrderingChanged(Orderable orderable) =>
        dispatchEvent(new CustomEvent('calculate.moved', detail: (orderable as LineItem).getCell(0)));

    onCalculationFinished(Cell changedCell) {

        if (changedCell.resolver.ranges == null) return;

        var matrix = new List.generate(rows.length, (i)=>[0,0,0]);

        for (var range in changedCell.resolver.ranges) {
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

    clearHighlighting([Event _]) {
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
