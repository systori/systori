import 'dart:html';
import 'dart:async';
import 'dart:convert';
import 'package:systori/inputs.dart';


String CSRFToken;
Repository repository;
ChangeManager changeManager;
Token tokenGenerator = new Token();


class ModelState {

    final Model model;
    final Map committed;
          Map pending;

    bool get isSaving => pending != null;

    ModelState(model) :
        model = model,
        committed = initialCommitted(model);

    static Map<String,dynamic> initialCommitted(Model model) =>
        model.hasPK
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
        var token = new DateTime.now().millisecondsSinceEpoch;
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

    bool get hasChildModels {
        for (var childType in childTypes) {
            if (childrenOfType(childType).isNotEmpty) {
                return true;
            }
        }
        return false;
    }
    bool get hasNoChildModels => !hasChildModels;

    bool get hasPK => pk != null;
    bool get hasNoPk => !hasPK;

    int get pk => int.parse(dataset['pk'], onError: (s)=>null);
    set pk(int id) => dataset['pk'] = id.toString();

    int get token => int.parse(dataset['token'], onError: (s)=>null);
    set token(int token) => dataset['token'] = token.toString();

    ModelState state;
    List<Input> inputs = [];
    DivElement editor;

    Model.created(): super.created() {
        if (!dataset.containsKey('pk')) dataset['pk'] = '';
        if (!dataset.containsKey('token')) dataset['token'] = tokenGenerator.next().toString();
        if (children.isEmpty) {
            TemplateElement template = document.querySelector('#${type}-template');
            var clone = document.importNode(template.content, true);
            append(clone);
        }
        editor = this.querySelector(":scope>.editor");
    }

    bool get canSave;

    attached() { state = new ModelState(this); }

    HtmlElement getView(String field) =>
        editor.querySelector(".${field}");

    Input getInput(String field) {
        var input = getView(field) as Input;
        assert(!inputs.contains(input));
        inputs.add(input);
        return input;
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
        var data = (isChanged && canSave) ? new Map.from(state.save()) : {};
        if (data.isNotEmpty) {
            updateVisualState('saving');
        }
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
            if (hasNoPk) {
                data['token'] = token;
            } else {
                data['pk'] = pk;
            }
        }
        return data;
    }

    rollback() {
        updateVisualState('changed');
        if (state.isSaving) state.rollback();
        for (var childType in childTypes) {
            childrenOfType(childType).map((Model m) => m.rollback());
        }
    }

    commit(Map result) {
        updateVisualState('saved');
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

    delete() {
        if (pk != null) changeManager.delete(type, pk);
        remove();
    }

    maybeChildrenChanged() {
        for (var childType in childTypes) {
            for (var child in childrenOfType(childType)) {
                child.updateVisualState('changed');
            }
        }
    }

    updateVisualState(String state) {
        switch(state) {
            case 'changed':
                if (!editor.classes.contains(state) && isChanged) {
                    editor.classes = ['editor', 'changed'];
                }
                break;
            case 'saving':
                editor.classes = ['editor', 'saving'];
                break;
            case 'saved':
                editor.classes = ['editor'];
                break;
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
            sendData: JSON.encode(data, toEncodable: (o) => o is Set ? o.toList(): o)
        );
        return JSON.decode(response.responseText);
    }

    Future<Map> info(String model, String id) async {
        var response = await HttpRequest.request(
            "/api/editor/info/$model/$id",
            method: "GET",
            requestHeaders: headers,
        );
        return JSON.decode(response.responseText);
    }

    Future<List<Map>> search(Map<String,String> criteria) async {
        var response = await HttpRequest.request(
            "/api/editor/search",
            method: "POST",
            requestHeaders: headers,
            sendData: JSON.encode(criteria)
        );
        return JSON.decode(response.responseText);
    }

    Future<String> clone(Map<String,String> params) async {
        var response = await HttpRequest.request(
            "/api/editor/clone",
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
    Map<String,Set<int>> deletes = {};
    Map<String,Set<int>> pendingDeletes = {};
    ChangeManager(this.root);

    startAutoSync() =>
        timer = new Timer.periodic(new Duration(seconds: 5), (_)=>save());

    Completer saving;
    Completer saveRequest;

    Future _save() async {
        try {
            var data = root.save();
            if (deletes.isNotEmpty) {
                data['delete'] = deletes;
                pendingDeletes = deletes;
                deletes = {};
            }
            if (data.isNotEmpty) {
                Map response = await repository.save(root.pk, data);
                root.commit(response);
            }
            pendingDeletes = {};
            saving.complete();
        } catch (e) {
            root.rollback();
            rollbackDeletes();
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

    rollbackDeletes() {
        for (var objectType in pendingDeletes.keys) {
            deletes
                .putIfAbsent(objectType, ()=>new Set())
                .addAll(pendingDeletes[objectType]);
        }
        pendingDeletes = {};
    }

    delete(String objectType, int pk) {
        deletes.putIfAbsent(objectType+'s', ()=>new Set()).add(pk);
    }

}
