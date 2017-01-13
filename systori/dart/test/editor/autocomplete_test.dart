@TestOn('browser')
import 'dart:html';
import 'dart:async';
import 'package:test/test.dart';
import 'package:systori/editor.dart';
import 'package:systori/inputs.dart';
import 'tools.dart';


class Thing extends Model {

    String completedId;

    Input name;

    Thing.created(): super.created();

    attached() {
        name = getInput('name');
        name.addHandler(new AutocompleteKeyboardHandler(this,
            {}, (String id) => completedId = id
        ));
        super.attached();
    }

}


main() {
    tokenGenerator = new FakeToken();
    document.registerElement('sys-input', Input);
    document.registerElement('sys-thing', Thing);
    document.registerElement('sys-autocomplete', Autocomplete);

    Scaffolding scaffolding = new Scaffolding(querySelector('#scaffolding'));
    KeyboardNavigator nav = new KeyboardNavigator();
    FakeRepository fakeRepository;
    Thing thing;

    setUp(() {
        tokenGenerator = new FakeToken();
        fakeRepository = repository = new FakeRepository();
        scaffolding.reset();
        thing = querySelector('sys-thing');
        autocomplete = document.createElement('sys-autocomplete');
    });

    group("Autocomplete", () {

        test("search state", () async {
            thing.name.focus();
            expect(autocomplete.searching, isFalse);
            expect(autocomplete.searchRequested, isFalse);

            nav.sendText('a');
            await new Future.value();
            expect(autocomplete.searching, isTrue);
            expect(autocomplete.searchRequested, isFalse);

            nav.sendText('a');
            await new Future.value();
            expect(autocomplete.searching, isTrue);
            expect(autocomplete.searchRequested, isTrue);
        });

        test("basic use case", () async {
            thing.name.focus();
            nav.sendText('a');
            await new Future.value();
            expect(autocomplete.innerHtml, isEmpty);
            await fakeRepository.complete();
            expect(autocomplete.innerHtml, isNotEmpty);
            nav.sendDown();
            nav.sendEnter();
            expect(thing.completedId, '42');
        });

    });

}

