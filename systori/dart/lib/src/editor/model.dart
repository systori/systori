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

    bool hasDirtyChildren = false;
    bool get isChanged => state.delta.isNotEmpty;
    Map save() {
        var data = new Map.from(state.save());
        if (pk == null) {
            data['token'] = token;
        }
        if (hasDirtyChildren) {
            for (var childType in childTypes) {
                var dirtyChildren = [];
                for (Model child in this.querySelectorAll(':scope>sys-$childType')) {
                    if (child.isChanged || child.hasDirtyChildren) {
                        dirtyChildren.add(child.save());
                    }
                }
                if (dirtyChildren.isNotEmpty) {
                    data['${childType}s'] = dirtyChildren;
                }
            }
        }
        return data;
    }

    setPKs(Map result) {
        pk = result['pk'];
        for (var childType in childTypes) {
            var listName = '${childType}s';
            if (result.containsKey(listName)) {
                for (Model child in this.querySelectorAll(':scope>sys-$childType')) {
                    for (Map childResult in result[listName]) {
                        print(child.token); print(childResult);
                        if (childResult['token'] == child.token) {
                            child.setPKs(childResult);
                        }
                    }
                }
            }
        }
    }

    Model getRootModelForCreate() {
        Model root = this;
        while (root.parent is Model) {
            if ((root.parent as Model).pk == null) {
                root = root.parent;
                root.hasDirtyChildren = true;
            } else {
                break;
            }
        }
        return root;
    }
}
