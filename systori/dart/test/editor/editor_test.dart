@TestOn('browser')
import 'dart:html';
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
    FakeRepository repository;

    setUp(() {
        tokenGenerator = new FakeToken();
        scaffold.reset();
        nav.reset();
        repository = new FakeRepository();
        changeManager = new ChangeManager(repository);
    });

    group("Keyboard", () {

        test("[enter]", () {

            expect(nav.activeModel.pk, 1);
            expect(nav.activeModel is Job, isTrue);

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Group, isTrue);

            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is Task, isTrue);

            nav.sendText('test task');
            nav.sendEnter();

            expect(nav.activeModel.pk, null);
            expect(nav.activeModel is LineItem, isTrue);
        });

    });

    group("ChangeManager", () {

        test("group successful update", () {

            Job job = querySelector('sys-job');

            expect(changeManager.save, isEmpty);
            expect(changeManager.saving, isEmpty);

            // job name is changed
            nav.sendText(' Changed');

            expect(changeManager.save.length, 1);
            expect(changeManager.saving, isEmpty);

            changeManager.sync();

            expect(changeManager.save, isEmpty);
            expect(changeManager.saving.length, 1);

            expect(job.state.committed, {'name': 'Test Job', 'description': ''});

            repository.complete();

            expect(job.state.committed, {'name': 'Test Job Changed', 'description': ''});

            expect(changeManager.save, isEmpty);
            expect(changeManager.saving, isEmpty);

        });

        test("group successful create", () {

            expect(changeManager.save, isEmpty);
            expect(changeManager.saving, isEmpty);

            nav.sendEnter();

            nav.sendText('group changed');

            expect(changeManager.save.length, 1);
            expect(changeManager.saving, isEmpty);

            changeManager.sync();

            expect(changeManager.save, isEmpty);
            expect(changeManager.saving.length, 1);

            Group group = nav.activeModel;

            expect(group.pk, null);
            expect(group.state.committed, {'name': '', 'description': ''});

            repository.complete();

            expect(group.pk, 1);
            expect(group.state.committed, {'name': 'group changed', 'description': ''});

            expect(changeManager.save, isEmpty);
            expect(changeManager.saving, isEmpty);

        });

        test("save() with new parent", () {

            nav.sendEnter();
            nav.sendEnter();

            nav.sendText('group changed');

            Group group = nav.activeModel;
            Group parentGroup = group.parentGroup;

            expect(changeManager.save, [group]);
            expect(changeManager.saving, isEmpty);

            changeManager.sync();

            expect(changeManager.save, [group]);
            expect(changeManager.saving, [parentGroup]);

            expect(group.pk, null);
            expect(parentGroup.pk, null);
            expect(group.state.pending, {'name': 'group changed'});
            expect(repository.lastRequestMap, {
                'token': 101, 'job': 1, 'parent': 1,
                'groups': [
                    {'token': 102, 'name': 'group changed', 'job': 1}
                ]
            });

            repository.complete();

            expect(parentGroup.pk, 1);
            expect(group.pk, 2);
        });

    });
}
