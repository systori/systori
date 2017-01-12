@TestOn('browser')
import 'dart:html';
import 'dart:async';
import 'package:test/test.dart';
import 'package:systori/editor.dart';
import 'package:systori/spreadsheet.dart';
import 'package:systori/decimal.dart';
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

    group("KeyboardHandler", () {

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
                expect(cell.value, new Decimal.parse(text), reason: reason);
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
