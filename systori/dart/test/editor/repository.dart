import 'dart:async';
import 'package:systori/editor.dart';


class FakeRequest {

    static int _group_pk;
    set group_pk(int pk) => _group_pk = pk;
    int get group_pk => _group_pk++;

    static int _task_pk;
    set task_pk(int pk) => _task_pk = pk;
    int get task_pk => _task_pk++;

    static int _lineitem_pk;
    set lineitem_pk(int pk) => _lineitem_pk = pk;
    int get lineitem_pk => _lineitem_pk++;

    static reset() {
        _group_pk = 1;
        _task_pk = 1;
        _lineitem_pk = 1;
    }

    final Map data;
    final String objectType;
    final Completer<Map> completer;

    FakeRequest(this.objectType, this.data):
        completer = new Completer.sync();

    fail() => completer.completeError('failed');

    complete() {
        var objectPK;
        if (data.containsKey('pk')) {
            objectPK = data['pk'];
        } else {
            switch (objectType) {
                case 'group':
                    objectPK = group_pk; break;
                case 'task':
                    objectPK = task_pk; break;
            }
        }
        completer.complete({
            'pk': objectPK
        });
    }

}


class FakeRepository implements Repository {

    List<FakeRequest> _requests = [];

    FakeRepository() {
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
        var request = new FakeRequest(model.type, model.save());
        _requests.add(request);
        return request.completer.future;
    }

    Future<bool> delete(Model model) {

    }
}
