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
    String format_task(String position) => _format(position, zfill[zfill.length-1]);
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
    bool get isEmpty => name.text.isEmpty;
    DivElement description;

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
            } else {
                Task child = this.querySelector(':scope>sys-task') as Task;
                if (child != null && child.isEmpty) {
                    child.name.focus();
                } else {
                    Task task = document.createElement('sys-task');
                    insertBefore(task, child);
                    updateCode();
                    task.name.focus();
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
        enumerate/*<Group>*/(this.querySelectorAll(':scope>sys-task'))
            .forEach((IndexedValue<Group> g) {
            g.value.order = g.index+1;
        });
    }

    createSibling() {
        Group group = document.createElement('sys-group');
        parent.insertBefore(group, nextElementSibling);
        group.generateGroups();
        (parent as Group).updateCode();
        group.name.focus();
    }

}


class HtmlCell extends HighlightableInput with Cell {

    String get canonical => dataset['canonical'] ?? "";
    set canonical(String canonical) => dataset['canonical'] = canonical;

    String get local => dataset['local'] ?? "";
    set local(String local) => dataset['local'] = local;

    String get resolved => dataset['resolved'] ?? "";
    set resolved(String resolved) => dataset['resolved'] = resolved;

    String get preview => dataset['preview'] ?? "";
    set preview(String preview) => dataset['preview'] = preview;

    bool get isFocused => document.activeElement == this;

    List<StreamSubscription<Event>> subscriptions = [];

    HtmlCell.created(): super.created();

    attached() {
        subscriptions = [
            onBlur.listen(handleBlur),
            onFocus.listen(handleFocus),
            onKeyUp.listen(handleInput),
        ];
    }

    handleFocus(Event event) {
        focused();
        dispatchCalculate('focused');
        if (isTextNumber) {
            new Timer(new Duration(milliseconds: 1), () {
                window.getSelection().selectAllChildren(this);
            });
        }
        doHighlighting();
    }

    static final List<String> COLORS = [
        '187,168,146', '238,114,95', '250,185,75', '0,108,124', '0,161,154', '183,219,193'
    ];

    handleInput(KeyboardEvent e) {
        if (e.keyCode == KeyCode.LEFT || e.keyCode == KeyCode.RIGHT) return;
        dispatchCalculate('changed');
        (parent.parent.parent as HtmlRow).markRedWhenAllColumnsSet();
        doHighlighting();
    }

    handleBlur([Event _]) =>
        blurred();

    dispatchCalculate(String event) =>
        dispatchEvent(new CustomEvent('calculate', detail: {'cell': this, 'event': event}));

    doHighlighting() {
        if (isTextEquation) {
            new Timer(new Duration(milliseconds: 1), () =>
                highlight(resolver.ranges.map((r) =>
                new Highlight(r.srcStart, r.srcEnd,
                    COLORS[r.result.group % COLORS.length]))
                )
            );
        }
    }

}


abstract class HtmlRow implements Row {

    HtmlCell qty;
    HtmlCell price;
    DivElement unit;
    bool get hasPercent => unit.text.contains('%');
    HtmlCell total;

    markRedWhenAllColumnsSet() {
        if (qty.isCanonicalNotBlank && price.isCanonicalNotBlank && total.isCanonicalNotBlank) {
            [qty,price,total].forEach((Element e)=>e.style.color = 'red');
        } else {
            [qty,price,total].forEach((Element e)=>e.style.color = null);
        }
    }

}


class TaskCell extends HtmlCell {
    TaskCell.created(): super.created();
}


class LineItemCell extends HtmlCell {
    LineItemCell.created(): super.created();
}


class Task extends Model with Row, TotalRow, HtmlRow {

    DivElement code;
    DivElement name;
    bool get isEmpty => name.text.isEmpty;
    DivElement diffRow;
    DivElement diffCell;

    Group get parentGroup => parent as Group;
    set order(int position) {
        dataset['order'] = position.toString();
        code.text = "${parentGroup.code.text}.${Job.JOB.structure.format_task(dataset['order'])}";
    }

    LineItemSheet sheet;

    Task.created(): super.created() {
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#task-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
        code = getView("code");
        name = getInput("name");
        name.onKeyDown.listen(handleKeyboard);
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        diffRow = this.querySelector(":scope> div.price-difference");
        diffCell = diffRow.querySelector(":scope> .total");
        sheet = this.querySelector(":scope > sys-lineitem-sheet");
        on['calculate'].listen((CustomEvent e) {
            if (sheet.total == null) sheet.calculate(qty);
            calculateTotal(sheet.total);
        });
    }

    handleKeyboard(KeyboardEvent e) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (isEmpty) {
                (parent as Group).createSibling();
                remove();
            } else {
                LineItem child = this.querySelector(':scope>sys-lineitem-sheet>sys-lineitem') as LineItem;
                if (child != null && child.isEmpty) {
                    child.name.focus();
                } else {
                    LineItem li = document.createElement('sys-lineitem');
                    this.querySelector(':scope>sys-lineitem-sheet').insertBefore(li, child);
                    li.name.focus();
                }
            }
        }
    }

    createSibling() {
        Task task = document.createElement('sys-task');
        parent.insertBefore(task, nextElementSibling);
        (parent as Group).updateCode();
        task.name.focus();
    }

    setDiff(Decimal diff) {
        print(diff.decimal);
        if (diff.isZero) {
            diffRow.style.visibility = 'hidden';
            diffCell.text = '0';
        } else {
            diffRow.style.visibility = 'visible';
            diffCell.text = diff.money;
        }
    }
}


class LineItem extends Model with Orderable, Row, HtmlRow {

    DivElement name;
    bool get isEmpty => name.text.isEmpty;

    LineItem.created(): super.created() {
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#lineitem-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
        name = getInput("name");
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        this.querySelectorAll(':scope>.editor>.editor-row>div[contenteditable]').onKeyDown.listen(handleKeyboard);
    }

    handleKeyboard(KeyboardEvent e) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (isEmpty) {
                (parent.parent as Task).createSibling();
                remove();
            } else {
                LineItem li = document.createElement('sys-lineitem');
                parent.insertBefore(li, nextElementSibling);
                li.name.focus();
            }
        }
    }

}


class LineItemSheet extends HtmlElement with OrderableContainer, Spreadsheet {

    List<LineItem> get rows => this.querySelectorAll(':scope>sys-lineitem');

    LineItemSheet.created(): super.created() {
        on['calculate'].listen((CustomEvent e) {
            Cell cell = (e.detail as Map)['cell'] as Cell;
            var event = (e.detail as Map)['event'];
            if (event == 'focused')
                calculate(cell, focused: true);
            else
                calculate(cell, focused: false);
        });
        addEventListener('blur', clearHighlighting, true);
    }

    onOrderingChanged(Orderable orderable) =>
        dispatchEvent(new CustomEvent('calculate.moved', detail: {'cell': rows[0].getCell(0), 'event': 'moved'}));

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
                        col.style.background = 'rgba(${HtmlCell.COLORS[group%HtmlCell.COLORS.length]},0.2)';
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
