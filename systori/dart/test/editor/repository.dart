import 'dart:async';
import 'package:systori/editor.dart';


class FakeRequest {

    static int _group_pk;
    int get group_pk => _group_pk++;

    static int _task_pk;
    int get task_pk => _task_pk++;

    static int _lineitem_pk;
    int get lineitem_pk => _lineitem_pk++;

    static reset() {
        _group_pk = 1;
        _task_pk = 1;
        _lineitem_pk = 1;
    }

    final Map data;
    final Completer<Map> completer;

    FakeRequest(this.data):
        completer = new Completer.sync();

    fail() => completer.completeError('failed');

    complete() {
        completer.complete({
            'id': data['id']
        });
    }

}


class FakeRepository implements Repository {

    List<FakeRequest> _requests = [];

    LocalRepository() {
        FakeRequest.reset();
    }

    fail() {
        _requests.forEach((request) => request.fail());
        _requests.clear();
    }

    complete() {
        _requests.forEach((request) {
             request.complete();
        });
        _requests.clear();
    }

    Future<Map> save(Model model) {
        var request = new FakeRequest(model.save());
        _requests.add(request);
        return request.completer.future;
    }

    Future<bool> delete(Model model) {

    }
}
