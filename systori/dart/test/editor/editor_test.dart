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
        changeManager = new ChangeManager(Job.JOB, repository);
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

            // job name is changed
            nav.sendText(' Changed');

            expect(changeManager.saving, isFalse);

            changeManager.save();

            expect(changeManager.saving, isTrue);

            expect(job.state.committed, {'name': 'Test Job', 'description': ''});

            repository.complete();

            expect(job.state.committed, {'name': 'Test Job Changed', 'description': ''});

            expect(changeManager.saving, isFalse);

        });

        test("group successful create", () {

            nav.sendEnter();

            nav.sendText('group changed');

            expect(changeManager.saving, isFalse);

            changeManager.save();

            expect(changeManager.saving, isTrue);

            Group group = nav.activeModel;

            expect(group.pk, null);
            expect(group.state.committed, {'name': '', 'description': ''});

            repository.complete();

            expect(group.pk, 1);
            expect(group.state.committed, {'name': 'group changed', 'description': ''});

            expect(changeManager.saving, isFalse);

        });

    });
}
