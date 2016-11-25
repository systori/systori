import 'dart:html';
import 'dart:async';


Token tokenGenerator = new Token();


class Input extends HtmlElement {
    String get name => className;
    StreamController<KeyEvent> controller = new StreamController<KeyEvent>(sync: true);
    Stream<KeyEvent> get onKeyEvent => controller.stream;
    Input.created(): super.created() {
        onKeyDown.listen((KeyboardEvent ke) {
            controller.add(new KeyEvent.wrap(ke));
        });
    }
}


class ModelState {

    final Model model;
    final Map committed;
          Map pending;

    bool get isSaving => pending != null;

    ModelState(model) :
        model = model,
        committed = inputMap(model.inputs);

    Map save() {
        assert(pending == null);
        pending = delta;
        return pending;
    }

    commit() {
        assert(pending != null);
        committed.addAll(pending);
        pending = null;
    }

    rollback() {
        assert(pending != null);
        pending = null;
    }

    Map get delta => inputMap(model.inputs.where((i) {
        if (pending != null && pending.containsKey(i.name))
            return pending[i.name] != i.text;
        return committed[i.name] != i.text;
    }));

    static Map inputMap(Iterable<Input> inputs) => new Map.fromIterable(
        inputs, key: (i)=>i.name, value: (i)=>i.text
    );

}


class Token {
    int _previous = 0;
    next() {
        var token = new DateTime.now().millisecondsSinceEpoch - 1479970650895;
        if (token <= _previous) {
            token = ++_previous;
        } else {
            _previous = token;
        }
        return token;
    }
}


abstract class Model extends HtmlElement {

    String get type => nodeName.toLowerCase().substring(4);

    List<String> childTypes = [];

    int get pk => int.parse(dataset['pk'], onError: (s)=>null);
    set pk(int id) => dataset['pk'] = id.toString();

    int get order => int.parse(dataset['order'], onError: (s)=>null);
    set order(int order) => dataset['order'] = order.toString();

    int get token => int.parse(dataset['token'], onError: (s)=>null);
    set token(int token) => dataset['token'] = token.toString();

    ModelState state;
    List<Input> inputs = [];

    Model.created(): super.created() {
        if (!dataset.containsKey('pk')) dataset['pk'] = '';
        if (!dataset.containsKey('order')) dataset['order'] = '';
        if (!dataset.containsKey('token')) dataset['token'] = tokenGenerator.next().toString();
    }

    attached() => state = new ModelState(this);

    HtmlElement getView(String field) =>
        this.querySelector(":scope>.editor .${field}");

    Input getInput(String field) {
        var div = getView(field);
        assert(!inputs.contains(div));
        inputs.add(div);
        return div;
    }

    bool get isChanged => state.delta.isNotEmpty;

    Iterable<Model> childrenOfType(String childType) sync* {
        var NODE_NAME = 'SYS-${childType.toUpperCase()}';
        for (Element child in children) {
            if (child.nodeName==NODE_NAME) {
                yield child;
            }
        }
    }

    Map save() {
        var data = isChanged ? new Map.from(state.save()) : {};
        for (var childType in childTypes) {
            var saveChildren = childrenOfType(childType)
                .map((Model model) => model.save())
                .where((Map m) => m.isNotEmpty)
                .toList();
            if (saveChildren.isNotEmpty) {
                data['${childType}s'] = saveChildren;
            }
        }
        if (data.isNotEmpty) {
            if (pk == null) {
                data['token'] = token;
            } else {
                data['pk'] = pk;
            }
        }
        return data;
    }

    rollback() {
        if (state.isSaving) state.rollback();
        for (var childType in childTypes) {
            childrenOfType(childType).map((Model m) => m.rollback());
        }
    }

    commit(Map result) {
        pk = result['pk'];
        if (state.isSaving) state.commit();
        for (var childType in childTypes) {
            var listName = '${childType}s';
            if (!result.containsKey(listName)) continue;
            for (Model child in childrenOfType(childType)) {
                for (Map childResult in result[listName]) {
                    if (childResult['pk'] == child.pk ||
                        childResult['token'] == child.token) {
                        child.commit(childResult);
                    }
                }
            }
        }
    }

}
