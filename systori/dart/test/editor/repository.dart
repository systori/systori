import 'dart:async';
import 'package:systori/editor.dart';


class FakeToken extends Token {
    int _previous = 100;
    next() => ++_previous;
}


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
        var result = {'token': data['token']};
        if (data.containsKey('pk')) {
            result['pk'] = data['pk'];
        } else {
            switch (objectType) {
                case 'group':
                    result['pk'] = group_pk;
                    if (data.containsKey('groups')) {
                        result['groups'] = [];
                        for (var group in data['groups']) {
                            result['groups'].add({'pk': group_pk, 'token': group['token']});
                        }
                    }
                    break;
                case 'task':
                    result['pk'] = task_pk; break;
            }
        }
        completer.complete(result);
    }

}


class FakeRepository extends Repository {

    List<FakeRequest> _requests = [];

    Map get lastRequestMap =>
        _requests.last.data;

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
