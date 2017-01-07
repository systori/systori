import 'dart:html';
import 'dart:async';
import 'dart:convert';


String CSRFToken;
Repository repository;
ChangeManager changeManager;
Token tokenGenerator = new Token();


abstract class KeyboardHandler {
    // Returning false will stop propagating the event to
    // subsequent handlers.
    bool onKeyEvent(KeyEvent e, Input input);
    onFocusEvent(Input input) {}
    onBlurEvent(Input input) {}
}


class Input extends HtmlElement {

    Map<String,dynamic> get values => {className: text};
    List<KeyboardHandler> _handlers = [];

    Input.created(): super.created() {
        onFocus.listen((Event) =>
            _handlers.forEach((h) => h.onFocusEvent(this))
        );
        onKeyDown.listen((KeyboardEvent ke) =>
            dispatchHandlers(new KeyEvent.wrap(ke))
        );
        onKeyUp.listen((KeyboardEvent ke) =>
            dispatchHandlers(new KeyEvent.wrap(ke))
        );
        onBlur.listen((Event) =>
            _handlers.forEach((h) => h.onBlurEvent(this))
        );
    }

    addHandler(KeyboardHandler handler) {
        _handlers.add(handler);
    }

    dispatchHandlers(KeyEvent e) {
        for (KeyboardHandler handler in _handlers) {
            if (!handler.onKeyEvent(e, this))
                break;
        }
    }

}


class ModelState {

    final Model model;
    final Map committed;
          Map pending;

    bool get isSaving => pending != null;

    ModelState(model) :
        model = model,
        committed = initialCommitted(model);

    static Map<String,dynamic> initialCommitted(Model model) =>
        model.pk != null
            ? inputMap(model.inputs)
            : new Map.fromIterable(inputMap(model.inputs).keys,
                key: (String key) => key, value: (String key) => ''
            );

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

    bool isChanged(field, value) {
        if (pending != null && pending.containsKey(field))
            return pending[field] != value;
        return committed[field] != value;
    }

    Map<String,dynamic> get delta {
        var result = <String,dynamic>{};
        inputMap(model.inputs).forEach((String key, dynamic value) {
            if (isChanged(key, value)) result[key] = value;
        });
        return result;
    }

    static Map<String,dynamic> inputMap(Iterable<Input> inputs) {
        var result = <String,dynamic>{};
        inputs.forEach((Input input) => result.addAll(input.values));
        return result;
    }

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

    List<String> get childTypes => [];

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

    attached() { state = new ModelState(this); }

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


class Repository {

    Map<String, String> headers;

    Repository() {
        headers = {
            "X-CSRFToken": CSRFToken,
            "Content-Type": "application/json"
        };
    }

    Future<Map> save(int jobId, Map data) async {
        var response = await HttpRequest.request(
            "/api/job/$jobId/editor/save",
            method: "POST",
            requestHeaders: headers,
            sendData: JSON.encode(data)
        );
        return JSON.decode(response.responseText);
    }

    Future<List<List>> search(Map<String,String> criteria) async {
        var response = await HttpRequest.request(
            "/api/editor/search",
            method: "POST",
            requestHeaders: headers,
            sendData: JSON.encode(criteria)
        );
        return JSON.decode(response.responseText);
    }

    Future<String> inject(Map<String,String> params) async {
        var response = await HttpRequest.request(
            "/api/editor/inject",
            method: "POST",
            requestHeaders: headers,
            sendData: JSON.encode(params)
        );
        return response.responseText;
    }
}


class ChangeManager {

    Timer timer;
    Model root;
    ChangeManager(this.root);

    startAutoSync() =>
        timer = new Timer.periodic(new Duration(seconds: 5), (_)=>save());

    Completer saving;
    Completer saveRequest;

    Future _save() async {
        try {
            var data = root.save();
            if (data.isNotEmpty) {
                Map response = await repository.save(root.pk, data);
                root.commit(response);
            }
            saving.complete();
        } catch (e) {
            root.rollback();
            saving.completeError(e);
        } finally {
            saving = saveRequest;
            saveRequest = null;
            if (saving != null) {
                _save();
            }

        }
    }

    Future save() {
        if (saving == null) {
            saving = new Completer();
            _save();
            return saving.future;
        } else {
            if (saveRequest == null)
                saveRequest = new Completer();
            return saveRequest.future;
        }
    }

}
