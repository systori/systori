@TestOn('browser')
import 'dart:html';
import 'package:test/test.dart';
import 'package:systori/src/editor/model.dart';
import '../scaffolding.dart';


class Thing extends Model {

    Input name;
    Input description;
    Input qty;

    Thing.created(): super.created();

    attached() {
        name = getInput('name');
        description = getInput('description');
        qty = getInput('qty');
        super.attached();
    }

}


main() {
    document.registerElement('sys-input', Input);
    document.registerElement('sys-thing', Thing);

    Scaffolding scaffolding = new Scaffolding(querySelector('#scaffolding'));
    Thing thing;

    setUp(() {
        scaffolding.reset();
        thing = querySelector('sys-thing');
    });

    group("ModelState", () {

        test("succesful workflow", () {

            // initial state: delta empty and committed equals inputs
            expect(thing.state.delta, {});
            expect(thing.state.pending, null);
            expect(thing.state.committed, {'name': '', 'description': '', 'qty': ''});

            thing.qty.text = '2';

            // input changes: delta reflects change, committed is unmodified
            expect(thing.state.delta, {'qty': '2'});
            expect(thing.state.pending, null);
            expect(thing.state.committed, {'name': '', 'description': '', 'qty': ''});

            thing.state.save();

            // state saved: delta empty, pending has changes, committed is unmodified
            expect(thing.state.delta, {});
            expect(thing.state.pending, {'qty': '2'});
            expect(thing.state.committed, {'name': '', 'description': '', 'qty': ''});

            thing.state.commit();

            // state committed: delta empty, pending null, committed is updated
            expect(thing.state.delta, {});
            expect(thing.state.pending, null);
            expect(thing.state.committed, {'name': '', 'description': '', 'qty': '2'});
        });

        test("edits while saving", () {

            thing.qty.text = '2';
            thing.state.save();

            // edit another field
            thing.name.text = 'bar';
            expect(thing.state.delta, {'name': 'bar'});
            expect(thing.state.pending, {'qty': '2'});
            expect(thing.state.committed, {'name': '', 'description': '', 'qty': ''});

            // edit same field that's being saved
            thing.qty.text = '3';
            expect(thing.state.delta, {'name': 'bar', 'qty': '3'});
            expect(thing.state.pending, {'qty': '2'});
            expect(thing.state.committed, {'name': '', 'description': '', 'qty': ''});

            // after commit, qty is still dirty
            thing.state.commit();
            expect(thing.state.delta, {'name': 'bar', 'qty': '3'});
            expect(thing.state.pending, null);
            expect(thing.state.committed, {'name': '', 'description': '', 'qty': '2'});

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
            expect(thing.state.committed, {'name': '', 'description': '', 'qty': ''});

        });

    });
}