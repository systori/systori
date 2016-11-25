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

    Future<Map> save(int jobId, Map data) async {
        var response = await HttpRequest.request(
            "/api/job/$jobId/editor/save",
            method: "POST",
            requestHeaders: headers,
            sendData: JSON.encode(data)
        );
        return JSON.decode(response.responseText);
    }

}


class ChangeManager {

    Timer timer;
    Model root;
    Repository repository;
    ChangeManager(this.root, this.repository);

    bool saving = false;

    startAutoSync() =>
        timer = new Timer.periodic(new Duration(seconds: 5), (_)=>save());

    save() {
        if (saving) return;
        saving = true;
        var data = root.save();
        if (data.isNotEmpty) {
            repository.save(root.pk, data)
                .then((Map response) {
                    root.commit(response);
                })
                .catchError((Error e) {
                    print(e);
                    root.rollback();
                })
                .whenComplete(() => saving = false);
        } else {
            saving = false;
        }
    }

}
