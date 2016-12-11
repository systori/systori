import 'dart:html';
import 'dart:async';
import 'package:intl/intl.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';
import 'package:systori/orderable.dart';
import 'package:systori/inputs.dart';
import 'model.dart';
import 'changemanager.dart';
import 'gaeb.dart';


ChangeManager changeManager;




class Job extends Group {
    static Job JOB;
    GAEBHierarchyStructure structure;
    int depth = 0;
    Job.created(): super.created() {
        structure = new GAEBHierarchyStructure(dataset['structure-format']);
        JOB = this;
    }
}


class Group extends Model {

    DivElement code;
    Input name;
    Input description;
    bool get isEmpty => name.text.isEmpty;

    List<String> childTypes = ['group', 'task'];
    Group get parentGroup => parent as Group;
    ElementList<Group> get groups => this.querySelectorAll(':scope>sys-group');
    ElementList<Task> get tasks => this.querySelectorAll(':scope>sys-task');
    int get depth => (parent as Group).depth + 1;

    set order(int position) {
        dataset['order'] = position.toString();
        code.text = "${parentGroup.code.text}.${Job.JOB.structure.formatGroup(dataset['order'], position)}";
    }

    Group.created(): super.created();

    attached() {
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#group-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
        code = getView("code");
        name = getInput("name");
        description = getInput("description");
        inputs.forEach((Input input) =>
            input.onKeyEvent.listen(handleKeyboard)
        );
        super.attached();
    }

    handleKeyboard(KeyEvent e) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (Job.JOB.structure.isValidDepth(depth+1)) {
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
        if (Job.JOB.structure.isValidDepth(depth+1)) {
            Group group = document.createElement('sys-group');
            children.add(group);
            group.generateGroups();
        }
    }

    updateCode() {
        enumerate<Group>(this.querySelectorAll(':scope>sys-group'))
            .forEach((IndexedValue<Group> g) {
            g.value.order = g.index+1;
            g.value.updateCode();
        });
        enumerate<Task>(this.querySelectorAll(':scope>sys-task'))
            .forEach((IndexedValue<Task> g) {
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


class HtmlCell extends Input with HighlightableInputMixin, Cell {

    Map<String,dynamic> get values => {
        className: text,
        '${className}_equation': canonical
    };

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
    Input unit;
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


class Task extends Model with Row, TotalRow, HtmlRow {

    List<String> childTypes = ['lineitem'];

    DivElement code;
    Input name;
    Input description;
    bool get isEmpty => name.text.isEmpty;
    DivElement diffRow;
    DivElement diffCell;

    Group get parentGroup => parent as Group;
    set order(int position) {
        dataset['order'] = position.toString();
        code.text = "${parentGroup.code.text}.${Job.JOB.structure.formatTask(dataset['order'])}";
    }

    LineItemSheet sheet;

    Task.created(): super.created() {
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#task-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
    }

    attached() {
        code = getView("code");
        name = getInput("name");
        description = getInput("description");
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        inputs.forEach((Input input) =>
            input.onKeyEvent.listen(handleKeyboard)
        );
        diffRow = this.querySelector(":scope> div.price-difference");
        diffCell = diffRow.querySelector(":scope> .total");
        sheet = this.querySelector(":scope > sys-lineitem-sheet");
        on['calculate'].listen((CustomEvent e) {
            if (sheet.total == null) sheet.calculate(qty);
            calculateTotal(sheet.total);
        });
        super.attached();
    }

    Iterable<Model> childrenOfType(String childType) =>
        this.querySelectorAll<Model>(":scope > sys-lineitem-sheet > sys-lineitem");

    handleKeyboard(KeyEvent e) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (isEmpty) {
                (parent as Group).createSibling();
                remove();
            } else {
                LineItem child = this.querySelector(':scope>sys-lineitem-sheet>sys-lineitem');
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
        parent.appendHtml('', treeSanitizer: NodeTreeSanitizer.trusted);
        (parent as Group).updateCode();
        task.name.focus();
    }

    setDiff(Decimal diff) {
        if (diff.isZero) {
            diffRow.style.visibility = 'hidden';
            diffCell.text = '0';
        } else {
            diffRow.style.visibility = 'visible';
            diffCell.text = diff.difference;
        }
    }

    getChanges() {
        return {};
    }
}


class LineItem extends Model with Orderable, Row, HtmlRow {

    Input name;
    bool get isEmpty => name.text.isEmpty;

    LineItem.created(): super.created() {
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#lineitem-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
    }

    attached() {
        name = getInput("name");
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        this.querySelectorAll(':scope>.editor [contenteditable]').onKeyDown.listen(handleKeyboard);
        super.attached();
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

    List<LineItem> get rows => this.querySelectorAll<LineItem>(':scope>sys-lineitem');

    LineItemSheet.created(): super.created() {
        on['calculate'].listen((CustomEvent e) {
            Cell cell = (e.detail as Map)['cell'] as Cell;
            var event = (e.detail as Map)['event'];
            if (event == 'focused')
                calculate(cell, focused: true);
            else if (event == 'moved')
                calculate(cell, moved: true);
            else
                calculate(cell);
        });
        addEventListener('blur', clearHighlighting, true);
    }

    onOrderingChanged(Orderable orderable) =>
        dispatchEvent(new CustomEvent('calculate', detail: {'cell': rows[0].getCell(0), 'event': 'moved'}));

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
                var col = row.getCell(colIdx) as HtmlCell;
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


registerElements() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    document.registerElement('sys-input', Input);
    document.registerElement('sys-cell', HtmlCell);
    document.registerElement('sys-lineitem', LineItem);
    document.registerElement('sys-lineitem-sheet', LineItemSheet);
    document.registerElement('sys-task', Task);
    document.registerElement('sys-job', Job);
    document.registerElement('sys-group', Group);
}
