import 'dart:html';
import 'dart:async';
import 'dart:convert';
import 'editor.dart';
import 'model.dart';


class Repository {

    Map<String, String> headers;

    Repository() {
        var csrftoken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
        headers = {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        };
    }

    Future<Map> save(Model model) {
        var model_api = model.type == 'job' ? 'group' : model.type;
        var wait_for_response;
        if (model.pk == null) {
            wait_for_response = HttpRequest.request(
                "/api/${model_api}/",
                method: "POST",
                requestHeaders: headers,
                sendData: JSON.encode(model.save())
            );
        } else {
            wait_for_response = HttpRequest.request(
                "/api/${model_api}/${model.pk}/",
                method: "PATCH",
                requestHeaders: headers,
                sendData: JSON.encode(model.save())
            );
        }

        var result = new Completer<Map>();
        wait_for_response.then((HttpRequest response) {
                result.complete(JSON.decode(response.responseText));
        }, onError: result.completeError);
        return result.future;

    }

    Future<bool> delete(Model model) {

    }

}


class ChangeManager {

    Timer timer;
    Repository repository;
    Set<Model> save = new Set();
    Set<Model> saving = new Set();
    Set<Model> delete = new Set();
    Set<Model> deleting = new Set();

    ChangeManager(this.repository);

    startAutoSync() =>
        timer = new Timer.periodic(new Duration(seconds: 5), (_)=>sync());

    sync() {

        if (saving.isNotEmpty) return;

        for (var model in delete) {
            deleting.add(model);
            repository.delete(model).then((result)=>deleting.remove(model));
        }
        delete = new Set();

        var stillPending = new Set();
        for (var model in save) {
            if (model.isChanged) {
                if (model.pk == null) {
                    var root = model.getRootModelForCreate();
                    if (root != model) {
                        stillPending.add(model);
                        if (!saving.contains(root)) {
                            saving.add(root);
                            repository.save(root).then(
                                (map)=>saved(map, root),
                                onError: (_)=>failed(root)
                            );
                        }
                        continue;
                    }
                }
                saving.add(model);
                repository.save(model).then(
                    (map)=>saved(map, model),
                    onError: (_)=>failed(model)
                );
            }
        }
        save = stillPending;
    }

    saved(Map result, Model model) {
        model.state.commit();
        model.setPKs(result);
        saving.remove(model);
    }

    failed(Model model) {
        model.state.rollback();
        saving.remove(model);
        save.add(model);
    }

    changed(Model model) => save.add(model);
    deleted(Model model) => delete.add(model);

}
