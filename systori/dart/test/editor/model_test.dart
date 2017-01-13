@TestOn('browser')
import 'dart:html';
import 'dart:async';
import 'package:test/test.dart';
import 'package:systori/editor.dart';
import 'package:systori/inputs.dart';
import 'tools.dart';


class Thing extends Model {

    bool get canSave => name.text.isNotEmpty;

    Input name;
    Input description;
    HtmlCell qty;

    List<String> childTypes = ['part'];

    Thing.created(): super.created();

    attached() {
        name = getInput('name');
        description = getInput('description');
        qty = getInput('qty');
        super.attached();
    }

}


class Part extends Model {

    bool get canSave => name.text.isNotEmpty;

    Input name;
    Input description;
    HtmlCell qty;

    Part.created(): super.created();

    attached() {
        name = getInput('name');
        description = getInput('description');
        qty = getInput('qty');
        super.attached();
    }

}


main() {
    tokenGenerator = new FakeToken();
    document.registerElement('sys-input', Input);
    document.registerElement('sys-cell', HtmlCell);
    document.registerElement('sys-part', Part);
    document.registerElement('sys-thing', Thing);

    Scaffolding scaffolding = new Scaffolding(querySelector('#scaffolding'));
    KeyboardNavigator nav = new KeyboardNavigator();
    FakeRepository fakeRepository;
    Thing thing;
    Part part;

    setUp(() {
        tokenGenerator = new FakeToken();
        scaffolding.reset();
        thing = querySelector('sys-thing');
        part = querySelector('sys-part');
        changeManager = new ChangeManager(thing);
        fakeRepository = repository = new FakeRepository();
    });

    group("ModelState", () {

        test("succesful workflow", () {
            // initial state: delta empty and committed equals inputs
            expect(thing.state.delta, {'qty': '0'});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': '', 'qty_equation': ''});

            thing.name.text = 'new';

            // input changes: delta reflects change, committed is unmodified
            expect(thing.state.delta, {'name': 'new', 'qty': '0'});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': '', 'qty_equation': ''});

            thing.state.save();

            // state saved: delta empty, pending has changes, committed is unmodified
            expect(thing.state.delta, {});
            expect(thing.state.pending, {'name': 'new', 'qty': '0'});
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': '', 'qty_equation': ''});

            thing.state.commit();

            // state committed: delta empty, pending null, committed is updated
            expect(thing.state.delta, {});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': 'new', 'description': '', 'qty': '0', 'qty_equation': ''});
        });

        test("edits while saving", () {
            thing.qty.text = '2';
            thing.state.save();

            // edit another field
            thing.name.text = 'bar';
            expect(thing.state.delta, {'name': 'bar'});
            expect(thing.state.pending, {'qty': '2'});
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': '', 'qty_equation': ''});

            // edit same field that's being saved
            thing.qty.text = '3';
            expect(thing.state.delta, {'name': 'bar', 'qty': '3'});
            expect(thing.state.pending, {'qty': '2'});
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': '', 'qty_equation': ''});

            // after commit, qty is still dirty
            thing.state.commit();
            expect(thing.state.delta, {'name': 'bar', 'qty': '3'});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': '2', 'qty_equation': ''});
        });

        test("save rolledback", () {
            thing.qty.text = '2';
            thing.state.save();
            expect(thing.state.delta, {});

            thing.name.text = 'bar';
            expect(thing.state.delta, {'name': 'bar'});

            thing.state.rollback();
            expect(thing.state.delta, {'name': 'bar', 'qty': '2'});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': '', 'qty_equation': ''});
        });

        test("state indicator class", () async {
            DivElement editor = thing.querySelector(':scope>div.editor');
            expect(editor.classes, ['editor']);
            thing.name.focus();
            nav.sendText('a');
            expect(editor.classes, ['editor', 'changed']);
            changeManager.save();
            await new Future.value();
            expect(editor.classes, ['editor', 'saving']);
            await fakeRepository.complete();
            expect(editor.classes, ['editor']);
        });

    });

}