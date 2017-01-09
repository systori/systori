import 'dart:html';
import 'dart:async';
import 'package:intl/intl.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/decimal.dart';
import 'package:systori/spreadsheet.dart';
import 'package:systori/orderable.dart';
import 'package:systori/inputs.dart';
import 'model.dart';
import 'gaeb.dart';
import 'autocomplete.dart';


class TextareaKeyboardHandler extends KeyboardHandler {
    /*
        Add this keyboard handler before any other handlers
        to multi-line textareas so that [Enter]+[Shift] could
        be used to enter new lines.
     */
    @override
    bool onKeyDownEvent(KeyEvent e, Input input) {
        if (e.keyCode == KeyCode.ENTER && e.shiftKey) {
            /* don't run any other handlers */
            return false;
        }
        return true;
    }
}


class Job extends Group {
    static Job JOB;
    GAEBHierarchyStructure structure;
    int depth = 0;
    Job.created(): super.created() {
        structure = new GAEBHierarchyStructure(dataset['structure-format']);
        JOB = this;
    }
    createSibling() => createChild();
}


class GroupKeyboardHandler extends KeyboardHandler {

    Group group;
    GroupKeyboardHandler(this.group);

    @override
    bool onKeyDownEvent(KeyEvent e, Input input) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (group.isBlank) {
                Group parent = group.parent as Group;
                group.remove();
                parent.createSibling();
            } else {
                group.createChild();
            }
            return false;
        }
        return true;
    }
}


class Group extends Model {

    DivElement code;
    Input name;
    Input description;

    List<String> childTypes = ['group', 'task'];
    Group get parentGroup => parent as Group;
    ElementList<Group> get groups => this.querySelectorAll(':scope>sys-group');
    ElementList<Task> get tasks => this.querySelectorAll(':scope>sys-task');
    int get depth => (parent as Group).depth + 1;

    bool get isBlank => hasNoPk && name.text.isEmpty;
    bool get canSave => name.text.isNotEmpty && autocomplete.input != name;

    set order(int position) {
        dataset['order'] = position.toString();
        code.text = "${parentGroup.code.text}.${Job.JOB.structure.formatGroup(dataset['order'], depth)}";
    }

    Group.created(): super.created();

    attached() {
        code = getView("code");
        name = getInput("name");
        name.addHandler(new AutocompleteKeyboardHandler(this, {
            'remaining_depth': Job.JOB.structure.remainingDepth(depth).toString()
        }, replaceWithCloneOf));
        description = getInput("description");
        description.addHandler(new TextareaKeyboardHandler());
        new GroupKeyboardHandler(this).bindAll(inputs);
        super.attached();
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
        Group newGroup = document.createElement('sys-group');
        parent.insertBefore(newGroup, nextElementSibling);
        (parent as Group).updateCode();
        newGroup.name.focus();
    }

    createChild() {
        if (Job.JOB.structure.isValidDepth(depth+1)) {
            Group group = document.createElement('sys-group');
            insertBefore(group, this.querySelector(':scope>sys-group'));
            updateCode();
            group.name.focus();
        } else {
            Task task = document.createElement('sys-task');
            insertBefore(task, this.querySelector(':scope>sys-task'));
            updateCode();
            task.name.focus();
        }
    }

    replaceWithCloneOf(String id) async {
        // make sure parent is saved and has pk
        await changeManager.save();
        var params = {
            'source_type': 'group',
            'source_pk': id,
            'target_pk': parentGroup.pk.toString(),
            'position': order.toString(),
        };
        var html = await repository.clone(params);
        var fragment = document.createDocumentFragment();
        fragment.setInnerHtml(html, treeSanitizer: NodeTreeSanitizer.trusted);
        var parent = this.parent;
        var idx = parent.children.indexOf(this);
        replaceWith(fragment.children[0]);
        (parent.children[idx] as Group).name.focus();
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


class TaskKeyboardHandler extends KeyboardHandler {

    Task task;
    TaskKeyboardHandler(this.task);

    @override
    bool onKeyDownEvent(KeyEvent e, Input input) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (task.isBlank) {
                Group parent = task.parent as Group;
                task.remove();
                parent.createSibling();
            } else {
                task.sheet.createChild();
            }
            return false;
        }
        return true;
    }
}


class Task extends Model with Row, TotalRow, HtmlRow {

    bool get isBlank => hasNoPk && name.text.isEmpty;
    bool get canSave => name.text.isNotEmpty && autocomplete.input != name;

    List<String> childTypes = ['lineitem'];

    DivElement code;
    Input name;
    Input description;
    DivElement diffRow;
    DivElement diffCell;

    Group get parentGroup => parent as Group;
    set order(int position) {
        dataset['order'] = position.toString();
        code.text = "${parentGroup.code.text}.${Job.JOB.structure.formatTask(dataset['order'])}";
    }

    LineItemSheet sheet;

    Task.created(): super.created();

    attached() {
        code = getView("code");
        name = getInput("name");
        name.addHandler(new AutocompleteKeyboardHandler(this, {}, replaceWithCloneOf));
        description = getInput("description");
        description.addHandler(new TextareaKeyboardHandler());
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        new TaskKeyboardHandler(this).bindAll(inputs);
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

    createSibling() {
        Task task = document.createElement('sys-task');
        parent.insertBefore(task, nextElementSibling);
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

    replaceWithCloneOf(String id) async {
        // make sure parent is saved and has pk
        await changeManager.save();
        var params = {
            'source_type': 'task',
            'source_pk': id,
            'target_pk': parentGroup.pk.toString(),
            'position': order.toString(),
        };
        var html = await repository.clone(params);
        var fragment = document.createDocumentFragment();
        fragment.setInnerHtml(html, treeSanitizer: NodeTreeSanitizer.trusted);
        var parent = this.parent;
        var idx = parent.children.indexOf(this);
        replaceWith(fragment.children[0]);
        (parent.children[idx] as Task).name.focus();
    }

}


class LineItemKeyboardHandler extends KeyboardHandler {

    LineItem li;
    LineItemKeyboardHandler(this.li);

    @override
    bool onKeyDownEvent(KeyEvent e, Input input) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (li.isBlank) {
                Task parent = li.parent.parent as Task;
                li.remove();
                parent.createSibling();
            } else {
                li.createSibling();
            }
            return false;
        }
        return true;
    }
}


class LineItem extends Model with Orderable, Row, HtmlRow {

    Input name;
    bool get isBlank => hasNoPk && name.text.isEmpty;
    bool get canSave => name.text.isNotEmpty && autocomplete.input != name;

    LineItem.created(): super.created();

    attached() {
        name = getInput("name");
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        new LineItemKeyboardHandler(this).bindAll(inputs);
        super.attached();
    }

    createSibling() {
        LineItem li = document.createElement('sys-lineitem');
        parent.insertBefore(li, nextElementSibling);
        li.name.focus();
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

    createChild() {
        LineItem li = document.createElement('sys-lineitem');
        insertBefore(li, this.querySelector(':scope>sys-lineitem'));
        li.name.focus();
    }

}


registerElements() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    CSRFToken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
    document.registerElement('sys-input', Input);
    document.registerElement('sys-cell', HtmlCell);
    document.registerElement('sys-lineitem', LineItem);
    document.registerElement('sys-lineitem-sheet', LineItemSheet);
    document.registerElement('sys-task', Task);
    document.registerElement('sys-job', Job);
    document.registerElement('sys-group', Group);
    document.registerElement('sys-autocomplete', Autocomplete);
}
