import 'dart:html';
import 'dart:async';
import 'package:intl/intl.dart';
import 'package:quiver/iterables.dart';
import 'package:systori/numbers.dart';
import 'package:systori/spreadsheet.dart';
import 'package:systori/orderable.dart';
import 'package:systori/inputs.dart';
import 'model.dart';
import 'gaeb.dart';
import 'autocomplete.dart';
import 'stickyheader.dart';
import 'navigation.dart';


class TextareaKeyboardHandler extends KeyboardHandler {
    /*
        Add this keyboard handler before any other handlers
        to multi-line textareas so that [Enter]+[Shift] could
        be used to enter new lines.
     */
    @override
    bool onKeyDownEvent(KeyEvent e, TextInput input) {
        if (e.keyCode == KeyCode.ENTER && e.shiftKey) {
            /* don't run any other handlers */
            return true;
        }
        return false;
    }
}


class Job extends Group {
    static Job JOB;
    StickyHeader stickyHeader;
    GAEBHierarchyStructure structure;
    int depth = 0;

    Job.created(): super.created() {
        new StickyHeader(this);
        structure = new GAEBHierarchyStructure(dataset['structure-format']);
        JOB = this;
    }

    createSibling() => createChild();
    calculationChanged() => updateTotal();
}


class DecimalElement extends HtmlElement {
    Decimal _decimal;
    Decimal get value {
        if (_decimal == null)
            _decimal = new Decimal.parse(text, 3);
        return _decimal;
    }
    set value(Decimal d) {
        _decimal = d;
        text = d.money;
    }
    DecimalElement.created(): super.created();
}


class GroupArrowKeyHandler extends ArrowNavigationHandler {
    static var MAP = ArrowNavigationHandler.buildNavigationMap([
        ['name'],
        ['description']
    ]);
    GroupArrowKeyHandler(Group group): super(MAP, group);
}


class Group extends Model with KeyboardHandler {

    CodeInput code;
    TextInput name;
    TextInput description;
    DecimalElement total;

    List<String> childTypes = ['group', 'task'];
    Group get parentGroup => parent as Group;
    ElementList<Group> get groups => this.querySelectorAll(':scope>sys-group');
    ElementList<Task> get tasks => this.querySelectorAll(':scope>sys-task');
    int get depth => (parent as Group).depth + 1;

    bool get isBlank => hasNoPk && name.text.isEmpty;
    bool get canSave => name.text.isNotEmpty && autocomplete.input != name;

    Group.created(): super.created();

    ready() {
        total = getView("total");
        name = getInput("name");
        name.addKeyHandler(new AutocompleteKeyboardHandler(this, () => {
            'remaining_depth': Job.JOB.structure.remainingDepth(depth).toString()
        }, replaceWithCloneOf));
        description = getInput("description");
        description.addKeyHandler(new TextareaKeyboardHandler());
        bindAll(inputs.values);
        new GroupArrowKeyHandler(this);
        /* add these inputs after we bind all TextInputs */
        code = getInput("code");
    }

    updateCode() {
        enumerate<Group>(this.querySelectorAll(':scope>sys-group'))
            .forEach((IndexedValue<Group> g) {
            g.value.code.position = g.index+1;
            g.value.updateCode();
        });
        enumerate<Task>(this.querySelectorAll(':scope>sys-task'))
            .forEach((IndexedValue<Task> t) {
            t.value.code.position = t.index+1;
        });
        maybeChildrenChanged();
    }

    updateTotal() {
        var _total = new Decimal(0, 3);
        for (Group g in this.querySelectorAll(':scope>sys-group')) {
            _total += g.total.value;
        }
        for (Task t in this.querySelectorAll(':scope>sys-task')) {
            if (t.exclude_from_total) continue;
            _total += t.total.value;
        }
        total.value = _total;
    }

    calculationChanged() {
        updateTotal();
        parentGroup.calculationChanged();
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
            'position': code.position.toString(),
        };
        var html = await repository.clone(params);
        var fragment = document.createDocumentFragment();
        fragment.setInnerHtml(html, treeSanitizer: NodeTreeSanitizer.trusted);
        var parent = this.parent;
        var idx = parent.children.indexOf(this);
        replaceWith(fragment.children[0]);
        (parent.children[idx] as Group).name.focus();
    }

    @override
    bool onKeyDownEvent(KeyEvent e, TextInput input) {
        switch (e.keyCode) {
            case KeyCode.ENTER:
                e.preventDefault();
                if (isBlank) {
                    if (parent is! Job) {
                        Group this_parent = parent as Group;
                        remove();
                        this_parent.createSibling();
                    }
                } else {
                    createChild();
                }
                return true;
            case KeyCode.DELETE:
                if (!e.shiftKey || this is Job) break;
                e.preventDefault();
                Group this_parent = parent;
                Group next_focus;
                if (nextElementSibling is Group) {
                    next_focus = nextElementSibling;
                } else if (previousElementSibling is Group) {
                    next_focus = previousElementSibling;
                } else {
                    next_focus = this_parent;
                }
                delete();
                next_focus.name.scrollIntoView();
                next_focus.name.focus();
                this_parent.updateCode();
                return true;
        }
        return false;
    }

    @override
    bool onInputEvent(Input input) =>
        updateVisualState('changed');

}


class CodeInput extends Input {
    Map<String,dynamic> get values => {'order': position};
    int get position => int.parse(dataset['order'], onError: (s)=>null);
    set position(int position) {
        dataset['order'] = position.toString();
        var model = parent.parent.parent;
        if (model is Task) {
            text = "${model.parentGroup.code.text}.${Job.JOB.structure.formatTask(dataset['order'])}";
        } else if (model is Group) {
            text = "${model.parentGroup.code.text}.${Job.JOB.structure.formatGroup(dataset['order'], model.depth)}";
        } // lineitem doesn't display any code
    }
    CodeInput.created(): super.created();
}


class HtmlCell extends TextInput with HighlightableInputMixin, Cell, KeyboardHandler {

    Map<String,dynamic> get values => {
        className: value.canonical,
        '${className}_equation': canonical
    };

    String get canonical => dataset['canonical'] ?? "";
    set canonical(String canonical) => dataset['canonical'] = canonical;

    String get local => dataset['local'] ?? "";
    set local(String local) => dataset['local'] = local;

    String get resolved => dataset['resolved'] ?? "";
    set resolved(String resolved) {
        if (resolved == "") {
            dataset.remove('resolved');
        } else {
            dataset['resolved'] = resolved;
        }
    }

    String get preview => dataset['preview'] ?? "";
    set preview(String preview) {
        if (preview == "") {
            dataset.remove('preview');
        } else {
            dataset['preview'] = preview;
        }
    }

    bool get isFocused => document.activeElement == this;

    HtmlCell.created(): super.created() {
        addKeyHandler(this);
        if (value == null) {
            value = isTextNumber ? new Decimal.parse(text, 3) : new Decimal(null, 3);
        }
    }

    @override
    onFocusEvent(TextInput cell) {
        focused();
        (parent.parent.parent as HtmlRow).onCalculate('focused', this);
        if (isTextNumber) {
            new Timer(new Duration(milliseconds: 1), () {
                window.getSelection().selectAllChildren(this);
            });
        }
        doHighlighting();
    }

    @override
    onBlurEvent(TextInput cell) => blurred();

    static final List<String> COLORS = [
        '187,168,146', '238,114,95', '250,185,75', '0,108,124', '0,161,154', '183,219,193'
    ];

    @override
    onInputEvent(Input cell) {
        (parent.parent.parent as HtmlRow).onCalculate('changed', this);
        (parent.parent.parent as HtmlRow).markRedWhenAllColumnsSet();
        doHighlighting();
    }

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
    TextInput unit;
    bool get hasPercent => unit.text.contains('%');
    HtmlCell total;

    markRedWhenAllColumnsSet() {
        if (qty.isCanonicalNotBlank && price.isCanonicalNotBlank && total.isCanonicalNotBlank) {
            [qty,price,total].forEach((Element e)=>e.style.color = 'red');
        } else {
            [qty,price,total].forEach((Element e)=>e.style.color = null);
        }
    }

    onCalculate(String event, Cell cell);

}


class TaskArrowKeyHandler extends ArrowNavigationHandler {
    static var MAP = ArrowNavigationHandler.buildNavigationMap([
        ['name', 'qty', 'unit', 'price', 'total'],
        ['description']
    ]);
    TaskArrowKeyHandler(Task task): super(MAP, task);
}


class VariantInput extends TextInput with KeyboardHandler {

    static final VALID_INPUT = "0123456789.".codeUnits;

    Map<String,dynamic> get values => {
        'variant_group': dataset['group'],
        'variant_serial': dataset['serial']
    };

    int get group => int.parse(dataset['group'], onError: (s)=>0);
    int get serial => int.parse(dataset['serial'], onError: (s)=>0);

    VariantInput.created(): super.created() {
        addKeyHandler(this);
    }

    @override
    bool onKeyPressEvent(KeyEvent e, TextInput input) {
        if (!VALID_INPUT.contains(e.charCode)) {
            e.preventDefault();
            return true;
        }
        return false;
    }

    @override
    onInputEvent(Input input) {
        if (text.contains('.')) {
            var parts = text.split('.');
            dataset['group'] = parts[0].length > 0 ? parts[0]: '0';
            dataset['serial'] = parts[1].length > 0 ? parts[1] : '0';
        } else {
            dataset['group'] = text.length > 0 ? text : '0';
            dataset['serial'] = '0';
        }
    }

    @override
    onBlurEvent(Input input) {
        if (dataset['group'] != '0') {
            text = "${dataset['group']}.${dataset['serial']}";
        }
    }
}


class Task extends Model with Row, TotalRow, HtmlRow, KeyboardHandler {

    bool get isBlank => hasNoPk && name.text.isEmpty;
    bool get canSave => name.text.isNotEmpty && autocomplete.input != name;

    List<String> childTypes = ['lineitem'];

    CodeInput code;
    TextInput name;
    TextInput description;
    VariantInput variant;
    Toggle is_provisional_toggle;
    bool get is_provisional => is_provisional_toggle.value;
    bool get exclude_from_total => is_provisional || variant.serial > 0;
    DivElement diffRow;
    DivElement diffCell;

    Group get parentGroup => parent as Group;

    LineItemSheet sheet;

    Task.created(): super.created();

    ready() {
        name = getInput("name");
        name.addKeyHandler(new AutocompleteKeyboardHandler(this, ()=>{}, replaceWithCloneOf));
        variant = getInput("variant");
        description = getInput("description");
        description.addKeyHandler(new TextareaKeyboardHandler());
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        bindAll(inputs.values);
        new TaskArrowKeyHandler(this);
        /* add these inputs after we bind all TextInputs */
        code = getInput("code");
        is_provisional_toggle = getInput("is_provisional")..addHandler(this);

        diffRow = this.querySelector(":scope> div.price-difference");
        diffCell = diffRow.querySelector(":scope> .total");
        sheet = this.querySelector(":scope> sys-lineitem-sheet");
    }

    onCalculate(String event, Cell cell) {
        //if (sheet.total == null) sheet.calculate(qty);
        sheet.calculate(cell);
        calculateTotal(sheet.total);
        (parent as Group).calculationChanged();
        /*
        calculateTotal(sheet.total);
        if (event == 'focused')
            sheet.calculate(cell, focused: true);
        else
            sheet.calculate(cell);
            */
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
            'position': code.position.toString(),
        };
        var html = await repository.clone(params);
        var fragment = document.createDocumentFragment();
        fragment.setInnerHtml(html, treeSanitizer: NodeTreeSanitizer.trusted);
        var parent = this.parent;
        var idx = parent.children.indexOf(this);
        replaceWith(fragment.children[0]);
        (parent.children[idx] as Task).name.focus();
    }

    @override
    bool onKeyDownEvent(KeyEvent e, TextInput input) {
        switch(e.keyCode) {
            case KeyCode.ENTER:
                e.preventDefault();
                if (isBlank) {
                    Group p = parentGroup;
                    remove();
                    p.createSibling();
                } else {
                    sheet.createChild();
                }
                return true;
            case KeyCode.DELETE:
                if (!e.shiftKey) break;
                e.preventDefault();
                Group this_parent = parent;
                if (nextElementSibling is Task) {
                    (nextElementSibling as Task).name.scrollIntoView();
                    (nextElementSibling as Task).name.focus();
                } else if (previousElementSibling is Task) {
                    (previousElementSibling as Task).name.scrollIntoView();
                    (previousElementSibling as Task).name.focus();
                } else {
                    this_parent.name.scrollIntoView();
                    this_parent.name.focus();
                }
                delete();
                this_parent.updateCode();
                return true;
        }
        return false;
    }

    @override
    bool onInputEvent(Input input) {
        if (['is_provisional', 'variant'].contains(input.name)) {
            classes.toggle('excluded', exclude_from_total);
            parentGroup.calculationChanged();
        }
        return updateVisualState('changed');
    }

}


class LineItemArrowKeyHandler extends ArrowNavigationHandler {
    static var MAP = ArrowNavigationHandler.buildNavigationMap([
        ['name', 'qty', 'unit', 'price', 'total'],
    ]);
    LineItemArrowKeyHandler(LineItem li): super(MAP, li);
}


class LineItem extends Model with Orderable, Row, HtmlRow, KeyboardHandler {

    CodeInput dragHandle;
    TextInput name;
    Toggle is_hidden_toggle;
    Toggle is_flagged_toggle;
    bool get is_hidden => is_hidden_toggle.value;
    bool get is_flagged => is_flagged_toggle.value;
    bool get isBlank => hasNoPk && name.text.isEmpty;
    bool get canSave => name.text.isNotEmpty && autocomplete.input != name;

    LineItem.created(): super.created();

    ready() {
        name = getInput("name");
        qty = getInput("qty");
        unit = getInput("unit");
        price = getInput("price");
        total = getInput("total");
        bindAll(inputs.values);
        new LineItemArrowKeyHandler(this);
        /* add these inputs after we bind all TextInputs */
        dragHandle = getInput("sys-lineitem-handle");
        is_hidden_toggle = getInput("is_hidden")..addHandler(this);
        is_flagged_toggle = getInput("is_flagged")..addHandler(this);
    }

    createSibling() {
        LineItem li = document.createElement('sys-lineitem');
        parent.insertBefore(li, nextElementSibling);
        li.name.focus();
    }

    onCalculate(String event, Cell cell) =>
        (parent.parent as Task).onCalculate(event, cell);

    @override
    bool onKeyDownEvent(KeyEvent e, TextInput input) {
        LineItemSheet sheet_parent = parent as LineItemSheet;
        Task task_parent = sheet_parent.parent as Task;
        switch(e.keyCode) {
            case KeyCode.ENTER:
                e.preventDefault();
                if (isBlank) {
                    remove();
                    task_parent.createSibling();
                } else {
                    createSibling();
                }
                sheet_parent.onOrderingChanged();
                return true;
            case KeyCode.DELETE:
                if (!e.shiftKey) break;
                e.preventDefault();
                if (nextElementSibling is LineItem) {
                    (nextElementSibling as LineItem).name.focus();
                } else if (previousElementSibling is LineItem) {
                    (previousElementSibling as LineItem).name.focus();
                } else {
                    task_parent.name.focus();
                }
                delete();
                sheet_parent.onOrderingChanged();
                return true;
        }
        return false;
    }

    @override
    bool onInputEvent(Input input) {
        if (input.name == 'is_hidden') {
            onCalculate('hidden', total);
        }
        return updateVisualState('changed');
    }

    Model firstAbove() =>
        previousElementSibling is Model
            ? previousElementSibling
            : parent.parent;

    Model firstBelow() {
        // now try siblings
        if (nextElementSibling is Model) {
            return nextElementSibling;
        }
        // visit the ancestors
        var ancestor = parent.parent;
        while (ancestor is Model) {
            var sibling = ancestor.nextElementSibling;
            if (sibling is Model) {
                return sibling;
            }
            ancestor = ancestor.parent;
        }
        return null;
    }
}


class LineItemSheet extends HtmlElement with OrderableContainer, Spreadsheet {

    Task get task => parent;

    List<LineItem> get rows => this.querySelectorAll<LineItem>(':scope>sys-lineitem');

    LineItemSheet.created(): super.created() {
        addEventListener('blur', clearHighlighting, true);
    }

    onOrderingChanged([Orderable orderable]) {
        enumerate<LineItem>(rows).forEach((IndexedValue<LineItem> t) {
            t.value.dragHandle.position = t.index+1;
        });
        task.maybeChildrenChanged();
        task.onCalculate('moved', rows.isNotEmpty ? rows.first.getCell(0) : null);
    }

    onCalculationFinished(Cell changedCell) {

        if (changedCell == null || changedCell.resolver.ranges == null) return;

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
    document.registerElement('sys-decimal', DecimalElement);
    document.registerElement('sys-input', TextInput);
    document.registerElement('sys-toggle', Toggle);
    document.registerElement('sys-styled-input', StyledInput);
    document.registerElement('sys-code-input', CodeInput);
    document.registerElement('sys-variant-input', VariantInput);
    document.registerElement('sys-cell', HtmlCell);
    document.registerElement('sys-lineitem', LineItem);
    document.registerElement('sys-lineitem-sheet', LineItemSheet);
    document.registerElement('sys-task', Task);
    document.registerElement('sys-job', Job);
    document.registerElement('sys-group', Group);
    document.registerElement('sys-autocomplete', Autocomplete);
}
