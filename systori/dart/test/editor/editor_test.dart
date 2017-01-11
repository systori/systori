@TestOn('browser')
import 'dart:html';
import 'dart:async';
import 'package:test/test.dart';
import 'package:systori/editor.dart';
import 'navigator.dart';
import 'repository.dart';
import '../scaffolding.dart';


void main() {
    tokenGenerator = new FakeToken();
    registerElements();
    Scaffolding scaffold = new Scaffolding(querySelector('#editor-area'));
    KeyboardNavigator nav = new KeyboardNavigator();
    FakeRepository fakeRepository;

    setUp(() {
        tokenGenerator = new FakeToken();
        scaffold.reset();
        Job.JOB.name.focus();
        fakeRepository = repository = new FakeRepository();
        changeManager = new ChangeManager(Job.JOB);
        autocomplete = document.createElement('sys-autocomplete');
    });

    group("Keyboard", () {

        test("[enter]", () {

            expect(nav.activeModel.pk, 1);
            expect(nav.activeModel is Job, isTrue);
            expect((nav.activeModel as Job).depth, 0);

            nav.sendEnter();

            nav.sendText('first group');
            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).depth, 1);

            nav.sendEnter();

            nav.sendText('second group');
            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).depth, 2);

            nav.sendEnter();

            nav.sendText('first task');
            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Task, isTrue);

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is LineItem, isTrue);

            // blank models make [Enter] travel up the hierarchy

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Task, isTrue);

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).depth, 2);

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).depth, 1);

            // [Enter] in empty group just below root does nothing
            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).depth, 1);

        });

    });

    group("ChangeManager", () {

        test("group successful update", () async {

            Job job = querySelector('sys-job');

            // job name is changed
            nav.sendText(' Changed');

            expect(changeManager.saving, isNull);

            changeManager.save();

            await new Future.value(); // run event loop

            expect(changeManager.saving, new isInstanceOf<Completer>());

            expect(job.state.committed, {'name': 'Test Job', 'description': ''});

            await fakeRepository.complete();

            expect(job.state.committed, {'name': 'Test Job Changed', 'description': ''});

            expect(changeManager.saving, isNull);

        });

        test("group successful create", () async {

            nav.sendEnter();

            Group group = nav.activeModel;

            nav.sendText('group changed');
            group.description.focus(); // cannot save while focus is in name

            expect(changeManager.saving, isNull);

            changeManager.save();

            await new Future.value(); // run event loop

            expect(changeManager.saving, new isInstanceOf<Completer>());

            expect(group.pk, null);
            expect(group.state.committed, {'name': '', 'description': ''});

            await fakeRepository.complete();

            expect(group.pk, 1);
            expect(group.state.committed, {'name': 'group changed', 'description': ''});

            expect(changeManager.saving, isNull);

        });

    });

    group("Inject Autocompleted Result", () {

        test("basic use case", () async {
            nav.sendEnter();

            Group group = nav.activeModel;
            expect(group.pk, isNull);
            expect(group.hasChildModels, isFalse);

            nav.sendText('a');
            await fakeRepository.complete(); // repository.search()

            nav.sendDown(); // move into autocomplete dropdown
            nav.sendEnter(); // select first 'match'

            await fakeRepository.complete(); // repository.save()
            await fakeRepository.complete(); // repository.clone()

            Group newGroup = nav.activeModel;

            // injection replaces the active element with new one from server
            expect(newGroup, isNot(equals(group)));
            expect(newGroup.pk, 99);
        });

    });

    group("Calculation", () {

        test("Calculation propagates from lineitem all the way to job.", () {

            nav.sendEnter();
            nav.sendText('first group, depth 1');
            Group group1 = nav.activeModel;

            nav.sendEnter();
            nav.sendText('second group, depth 2');
            Group group2 = nav.activeModel;

            nav.sendEnter();
            nav.sendText('task one');
            Task task = nav.activeModel;
            task.qty.focus();
            nav.sendText('2');

            nav.sendEnter();
            nav.sendText('lineitem one');
            LineItem li = nav.activeModel;
            li.qty.focus();
            nav.sendText('5');
            li.price.focus();

            expect(li.total.value.decimal, 0);
            expect(task.price.value.decimal, 0);
            expect(task.total.value.decimal, 0);
            expect(group2.total.value.decimal, 0);
            expect(group1.total.value.decimal, 0);
            expect(Job.JOB.total.value.decimal, 0);

            nav.sendText('5');

            expect(li.total.value.decimal, 25);
            expect(task.price.value.decimal, 25);
            expect(task.total.value.decimal, 50);
            expect(group2.total.value.decimal, 50);
            expect(group1.total.value.decimal, 50);
            expect(Job.JOB.total.value.decimal, 50);

        });

    });

}
