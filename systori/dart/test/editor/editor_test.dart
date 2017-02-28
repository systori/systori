@TestOn('browser')
import 'dart:html';
import 'dart:async';
import 'package:test/test.dart';
import 'package:systori/editor.dart';
import 'package:systori/spreadsheet.dart';
import 'package:systori/numbers.dart';
import 'tools.dart';


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

    group("KeyboardHandler", () {

        test("cursor", () {
            Job job = nav.activeModel;

            expect(job.name.text, 'Test Job');
            expect(nav.caretOffset, 0);

            nav.sendText('A ');
            expect(job.name.text, 'A Test Job');
            expect(nav.caretOffset, 2);

            nav.caretToEnd();
            nav.sendText(' One');
            expect(job.name.text, 'A Test Job One');
            expect(nav.caretOffset, 14);

            nav.selectAll();
            nav.sendText('Rock Gym');
            expect(job.name.text, 'Rock Gym');
            expect(nav.caretOffset, 8);

            nav.caretOffset = 4;
            nav.sendText(' Climbing');
            expect(job.name.text, 'Rock Climbing Gym');
            expect(nav.caretOffset, 13);
        });

        test("[enter]", () {

            expect(nav.activeModel.pk, 1);
            expect(nav.activeModel is Job, isTrue);
            expect((nav.activeModel as Job).code.text, '1');
            expect((nav.activeModel as Job).depth, 0);

            nav.sendEnter();

            nav.sendText('first group');
            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).code.text, '1.01');
            expect((nav.activeModel as Group).depth, 1);

            nav.sendEnter();

            nav.sendText('second group');
            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).code.text, '1.01.01');
            expect((nav.activeModel as Group).depth, 2);

            nav.sendEnter();

            nav.sendText('first task');
            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Task, isTrue);
            expect((nav.activeModel as Task).code.text, '1.01.01.001');

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is LineItem, isTrue);

            // blank models make [Enter] travel up the hierarchy

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Task, isTrue);
            expect((nav.activeModel as Task).code.text, '1.01.01.002');

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).depth, 2);
            expect((nav.activeModel as Group).code.text, '1.01.02');

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).depth, 1);
            expect((nav.activeModel as Group).code.text, '1.02');

            // [Enter] in empty group just below root does nothing
            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);
            expect((nav.activeModel as Group).depth, 1);
            expect((nav.activeModel as Group).code.text, '1.02');

        });

        test("arrow navigation", () {
            expect(nav.activeModel is Job, isTrue);
            expect(nav.inputName, 'name');

            nav.sendDown(shiftKey: true);
            expect(nav.activeModel is Job, isTrue);
            expect(nav.inputName, 'description');

            nav.sendDown(shiftKey: true);
            expect(nav.activeModel is Group, isTrue);
            expect(nav.inputName, 'name');

            nav.sendDown(shiftKey: true);
            expect(nav.activeModel is Group, isTrue);
            expect(nav.inputName, 'description');

            nav.sendDown(shiftKey: true);
            expect(nav.activeModel is Task, isTrue);
            expect(nav.inputName, 'name');

            nav.sendRight(shiftKey: true);
            expect(nav.activeModel is Task, isTrue);
            expect(nav.inputName, 'qty');

            nav.sendRight(shiftKey: true);
            expect(nav.activeModel is Task, isTrue);
            expect(nav.inputName, 'unit');

            nav.sendRight(shiftKey: true);
            expect(nav.activeModel is Task, isTrue);
            expect(nav.inputName, 'price');

            nav.sendRight(shiftKey: true);
            expect(nav.activeModel is Task, isTrue);
            expect(nav.inputName, 'total');

            nav.sendDown(shiftKey: true);
            expect(nav.activeModel is LineItem, isTrue);
            expect(nav.inputName, 'total');

            nav.sendLeft(shiftKey: true);
            expect(nav.activeModel is LineItem, isTrue);
            expect(nav.inputName, 'price');

            nav.sendLeft(shiftKey: true); // unit
            nav.sendLeft(shiftKey: true); // qty

            nav.sendLeft(shiftKey: true);
            expect(nav.activeModel is LineItem, isTrue);
            expect(nav.inputName, 'name');

            nav.sendUp(shiftKey: true);
            expect(nav.activeModel is Task, isTrue);
            expect(nav.inputName, 'description');

            nav.sendUp(shiftKey: true);
            expect(nav.activeModel is Task, isTrue);
            expect(nav.inputName, 'name');

            nav.sendUp(shiftKey: true);
            expect(nav.activeModel is Group, isTrue);
            expect(nav.inputName, 'description');
        });

    });

    group("ChangeManager", () {

        test("test new line processing in text fields", () {

            Job.JOB.name.setInnerHtml('hello <br />world', treeSanitizer: NodeTreeSanitizer.trusted);
            Job.JOB.description.setInnerHtml('hello <br />world', treeSanitizer: NodeTreeSanitizer.trusted);
            expect(Job.JOB.state.delta, {
                'name': 'hello world',
                'description': 'hello <br />world',
            });

            Group group1 = Job.JOB.childrenOfType('group').first;
            Group group2 = group1.childrenOfType('group').first;
            Task task = group2.childrenOfType('task').first;

            task.name.setInnerHtml('hello <br />world', treeSanitizer: NodeTreeSanitizer.trusted);
            task.description.setInnerHtml('hello <br />world', treeSanitizer: NodeTreeSanitizer.trusted);
            expect(task.state.delta, {
                'name': 'hello world',
                'description': 'hello <br />world',
            });

        });

        test("group successful update", () async {

            Job job = nav.activeModel;

            // job name is changed
            nav.caretToEnd();
            nav.sendText(' Changed');

            expect(changeManager.saving, isNull);

            changeManager.save();

            await new Future.value(); // run event loop

            expect(changeManager.saving, new isInstanceOf<Completer>());

            expect(job.state.committed, {'name': 'Test Job', 'description': '', 'order': 1});

            await fakeRepository.complete();

            expect(job.state.committed, {'name': 'Test Job Changed', 'description': '', 'order': 1});

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
            expect(group.state.committed, {'name': '', 'description': '', 'order': ''});

            await fakeRepository.complete();

            expect(group.pk, 1);
            expect(group.state.committed, {'name': 'group changed', 'description': '', 'order': 1});

            expect(changeManager.saving, isNull);

        });

        test("group created shifts position of others", () async {

            nav.sendEnter();
            nav.sendText('new group');
            Group group = nav.activeModel;
            group.description.focus();

            changeManager.save();

            await new Future.value(); // run event loop

            expect(fakeRepository.lastRequestMap, {
                'pk': 1,
                'groups': [
                    {'order': 1, 'name': 'new group', 'token': 101},
                    {'order': 2, 'pk': 2} // previously first group moved to 'order': 2
                ],
            });

            await fakeRepository.complete();

        });

        test("group successful delete", () async {

            Group group1 = Job.JOB.childrenOfType('group').first;
            group1.name.focus();

            nav.sendDelete();
            expect(group1.parent, isNotNull);
            expect(changeManager.deletes, {});

            nav.sendDelete(shiftKey: true);
            expect(group1.parent, isNull);
            expect(changeManager.deletes, {'groups': [2]});

            changeManager.save();

            await new Future.value(); // run event loop

            expect(changeManager.deletes, {});
            expect(changeManager.pendingDeletes, {'groups': [2]});

            await fakeRepository.complete();

            expect(changeManager.deletes, {});
            expect(changeManager.pendingDeletes, {});
            expect(changeManager.saving, isNull);

        });

        test("task created shifts position of others", () async {

            Group group1 = Job.JOB.childrenOfType('group').first;
            Group group2 = group1.childrenOfType('group').first;
            group2.name.focus();
            nav.sendEnter();
            nav.sendText('new task');
            Task task2 = nav.activeModel;
            task2.description.focus();

            changeManager.save();

            await new Future.value(); // run event loop

            expect(fakeRepository.lastRequestMap, {
                'pk': 1,
                'groups': [{
                    'pk': 2,
                    'groups': [{
                        'pk': 3,
                        'tasks': [
                            {'order': 1, 'name': 'new task', 'token': 101, 'qty': '0', 'price': '0', 'total': '0'},
                            {'order': 2, 'pk': 1} // previously first task moved to 'order': 2
                        ],
                    }],
                }],
            });

            await fakeRepository.complete();

        });

        test("task successful delete", () async {

            Group group1 = Job.JOB.childrenOfType('group').first;
            Group group2 = group1.childrenOfType('group').first;
            Task task = group2.childrenOfType('task').first;

            task.name.focus();

            nav.sendDelete();
            expect(task.parent, isNotNull);
            expect(changeManager.deletes, {});

            nav.sendDelete(shiftKey: true);
            expect(task.parent, isNull);
            expect(changeManager.deletes, {'tasks': [1]});

            changeManager.save();

            await new Future.value(); // run event loop

            expect(changeManager.deletes, {});
            expect(changeManager.pendingDeletes, {'tasks': [1]});

            await fakeRepository.complete();

            expect(changeManager.deletes, {});
            expect(changeManager.pendingDeletes, {});
            expect(changeManager.saving, isNull);

        });

        test("lineitem successful delete", () async {

            Group group1 = Job.JOB.childrenOfType('group').first;
            Group group2 = group1.childrenOfType('group').first;
            Task task = group2.childrenOfType('task').first;
            LineItem li = task.childrenOfType('lineitem').first;

            li.name.focus();

            nav.sendDelete();
            expect(li.parent, isNotNull);
            expect(changeManager.deletes, {});

            nav.sendDelete(shiftKey: true);
            expect(li.parent, isNull);
            expect(changeManager.deletes, {'lineitems': [1]});

            changeManager.save();

            await new Future.value(); // run event loop

            expect(changeManager.deletes, {});
            expect(changeManager.pendingDeletes, {'lineitems': [1]});

            await fakeRepository.complete();

            expect(changeManager.deletes, {});
            expect(changeManager.pendingDeletes, {});
            expect(changeManager.saving, isNull);

        });

    });

    group("Autocomplete", () {

        test("select search result & clone into document tree", () async {
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

    group("Basic Spreadsheet", () {

        test("calculation propagation", () {
            nav.sendEnter();
            nav.sendText('first group, depth 1');
            Group group1 = nav.activeModel;

            nav.sendEnter();
            nav.sendText('second group, depth 2');
            Group group2 = nav.activeModel;

            nav.sendEnter();
            nav.sendText('task one');
            Task task = nav.activeModel;
            nav.sendEnter();
            nav.sendText('lineitem one');
            LineItem li = nav.activeModel;

            expect(li.total.text, '0,00');
            expect(task.price.text, '0,00');
            expect(task.total.text, '0,00');
            expect(group2.total.text, '0,00');
            expect(group1.total.text, '0,00');
            expect(Job.JOB.total.text, '14.996,00');

            task.qty.focus();
            nav.sendText('2');

            li.qty.focus();
            nav.sendText('5');
            li.price.focus();
            nav.sendText('5');

            expect(li.total.text, '25,00');
            expect(task.price.text, '25,00');
            expect(task.total.text, '50,00');
            expect(group2.total.text, '50,00');
            expect(group1.total.text, '50,00');
            expect(Job.JOB.total.text, '15.046,00');
        });

        test("blank task & lineitem row has valid defaults", () {
            Group group1 = Job.JOB.childrenOfType('group').first;
            Group group2 = group1.childrenOfType('group').first;
            group2.name.focus();
            nav.sendEnter();
            Task task = nav.activeModel;

            expect(task.qty.value, new Decimal(0));
            expect(task.price.value, new Decimal(0));
            expect(task.total.value, new Decimal(0));

            task.name.focus();
            nav.sendText('task one');
            nav.sendEnter();

            LineItem li = nav.activeModel;
            expect(li.qty.value, new Decimal(0));
            expect(li.price.value, new Decimal(0));
            expect(li.total.value, new Decimal(0));
        });

        test("blank task row has valid defaults", () {
            Group group1 = Job.JOB.childrenOfType('group').first;
            Group group2 = group1.childrenOfType('group').first;
            Task task = group2.childrenOfType('task').first;
            LineItem li = task.childrenOfType('lineitem').first;

            expect(group2.total.text, '14.996,00');

            li.name.focus();
            nav.sendEnter(); // blank li
            nav.sendEnter(); // new blank task

            task.qty.focus();
            nav.setText('3'); // update previous valid task, group should update

            expect(group2.total.text, '224,94');
        });

        test("re-calculation does not reset cursor position", () {
            Group group1 = Job.JOB.childrenOfType('group').first;
            Group group2 = group1.childrenOfType('group').first;
            Task task = group2.childrenOfType('task').first;
            LineItem li = task.childrenOfType('lineitem').toList()[1];

            li.qty.focus();
            expect(nav.caretOffset, 0);
            expect(li.qty.text, '!');

            nav.setText('(1/100)');
            expect(nav.caretOffset, 7);
            expect(li.qty.preview, '1 / 100 = 0,01');

            nav.caretOffset = 0;
            nav.sendText('!+');
            expect(nav.caretOffset, 2);
            expect(li.qty.preview, '0,1 + (1 / 100) = 0,11');

            nav.caretToEnd();
            nav.sendText('+!');
            expect(nav.caretOffset, 11);
            expect(li.qty.preview, '(0,1 + (1 / 100)) + 0,1 = 0,21');
        });

    });

    group("Isomorphic Spreadsheet", () {

        /*
          The goal of this set of tests is to make sure that
          the spreadsheet models pre-rendered on the server
          from previously saved data result in identically
          functional structures as the spreadsheet models
          freshly created on the client. There are quite
          a few differences in how the client side treats
          these two paths. Most obvious one is that when
          browser loads a large document it does not
          evaluate all spreadsheets, instead this is done
          lazily as-needed in contrast to newly client side
          created data which starts off with already
          evaluated spreadsheet.
         */

        Group root;
        Group group1;
        Task task1;
        LineItem lineitem1;
        LineItem lineitem2;
        LineItem lineitem3;

        spreadsheetTests() {

            testCell(Cell cell, String text, String reason) {
                expect(cell.text, text, reason: reason);
                expect(cell.value, new Decimal.parse(text, 3), reason: reason);
            }

            testRow(HtmlRow row, String qty, String unit, String price, String total) {
                testCell(row.qty, qty, 'qty');
                expect(row.unit.text, unit, reason: 'unit');
                testCell(row.price, price, 'price');
                testCell(row.total, total, 'total');
            }

            test("initial state", () {
                expect(lineitem1.name.text, 'Labor');
                testRow(lineitem1, '0,1', 'hr', '19,80', '1,98');
                expect(lineitem2.name.text, 'Equipment Rental');
                testRow(lineitem2, '0,1', 'hr', '50,00', '5,00');
                expect(lineitem3.name.text, 'Materials');
                testRow(lineitem3, '4', 'm', '17,00', '68,00');

                expect(task1.name.text, 'Fence');
                testRow(task1, '200', 'm²', '74,98', '14.996,00');

                expect(group1.total.text, '14.996,00');
                expect(root.total.text, '14.996,00');
            });

        }

        group("Generated Server Side", () {

            setUp(() {
                root = Job.JOB.childrenOfType('group').first;
                group1 = root.childrenOfType('group').first;
                task1 = group1.childrenOfType('task').first;
                var lineitems = task1.childrenOfType('lineitem').toList();
                lineitem1 = lineitems[0];
                lineitem2 = lineitems[1];
                lineitem3 = lineitems[2];
            });

            spreadsheetTests();

        });

        group("Generated Client Side", () {

            setUp(() {
                nav.sendEnter();
                nav.sendText('first group, depth 1');
                root = nav.activeModel;

                nav.sendEnter();
                nav.sendText('second group, depth 2');
                group1 = nav.activeModel;

                nav.sendEnter();
                nav.sendText('Fence');
                task1 = nav.activeModel;
                task1.qty.focus();
                nav.sendText('200');
                task1.unit.focus();
                nav.sendText('m²');

                nav.sendEnter();
                nav.sendText('Labor');
                lineitem1 = nav.activeModel;
                lineitem1.qty.focus();
                nav.sendText('0,1');
                lineitem1.unit.focus();
                nav.sendText('hr');
                lineitem1.price.focus();
                nav.sendText('18*1,1');

                nav.sendEnter();
                nav.sendText('Equipment Rental');
                lineitem2 = nav.activeModel;
                lineitem2.qty.focus();
                nav.sendText('!');
                lineitem2.unit.focus();
                nav.sendText('hr');
                lineitem2.price.focus();
                nav.sendText('50');

                nav.sendEnter();
                nav.sendText('Materials');
                lineitem3 = nav.activeModel;
                lineitem3.qty.focus();
                nav.sendText('4');
                lineitem3.unit.focus();
                nav.sendText('m');
                lineitem3.price.focus();
                nav.sendText('17');

                nav.sendEnter();
            });

            spreadsheetTests();

        });

    });

}
