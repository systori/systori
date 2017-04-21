@TestOn('browser')
import 'dart:html';
import 'dart:async';
import 'package:test/test.dart';
import 'package:systori/src/editor/model.dart';
import 'package:systori/inputs.dart';
import 'tools.dart';


class Thing extends Model with KeyboardHandler {

    bool get canSave => name.text.isNotEmpty;

    TextInput name;
    TextInput description;
    TextInput qty;

    List<String> childTypes = ['part'];

    Thing.created(): super.created();

    attached() {
        name = getInput('name');
        description = getInput('description');
        qty = getInput('qty');
        bindAll(inputs.values);
        super.attached();
    }

    @override
    bool onInputEvent(Input input) =>
        updateVisualState('changed');

}


class Part extends Model {

    bool get canSave => name.text.isNotEmpty;

    TextInput name;
    TextInput description;
    TextInput qty;

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
    document.registerElement('sys-input', TextInput);
    document.registerElement('sys-part', Part);
    document.registerElement('sys-thing', Thing);

    Scaffolding scaffolding = new Scaffolding(querySelector('#scaffolding'));
    KeyboardNavigator nav = new KeyboardNavigator();
    FakeRepository fakeRepository;
    Thing thing;

    setUp(() {
        tokenGenerator = new FakeToken();
        scaffolding.reset();
        thing = querySelector('sys-thing');
        changeManager = new ChangeManager(thing);
        fakeRepository = repository = new FakeRepository();
    });

    group("ModelState", () {

        test("succesful workflow", () {
            // initial state: delta empty and committed equals inputs
            expect(thing.state.delta, {'qty': '0'});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': ''});

            thing.name.text = 'new';

            // input changes: delta reflects change, committed is unmodified
            expect(thing.state.delta, {'name': 'new', 'qty': '0'});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': ''});

            thing.state.save();

            // state saved: delta empty, pending has changes, committed is unmodified
            expect(thing.state.delta, {});
            expect(thing.state.pending, {'name': 'new', 'qty': '0'});
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': ''});

            thing.state.commit();

            // state committed: delta empty, pending null, committed is updated
            expect(thing.state.delta, {});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': 'new', 'description': '', 'qty': '0'});
        });

        test("edits while saving", () {
            thing.qty.focus();
            nav.setText('2');
            thing.state.save();

            // edit another field
            thing.name.text = 'bar';
            expect(thing.state.delta, {'name': 'bar'});
            expect(thing.state.pending, {'qty': '2'});
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': ''});

            // edit same field that's being saved
            thing.qty.text = '3';
            expect(thing.state.delta, {'name': 'bar', 'qty': '3'});
            expect(thing.state.pending, {'qty': '2'});
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': ''});

            // after commit, qty is still dirty
            thing.state.commit();
            expect(thing.state.delta, {'name': 'bar', 'qty': '3'});
            expect(thing.state.pending, null);
            expect(thing.state.committed,
                {'name': '', 'description': '', 'qty': '2'});
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
                {'name': '', 'description': '', 'qty': ''});
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