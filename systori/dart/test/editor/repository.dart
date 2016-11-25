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
    final Completer<Map> completer;

    FakeRequest(this.data):
        completer = new Completer.sync();

    complete() => completer.complete(response('group', data));
    fail() => completer.completeError('failed');

    Map response(String objectType, Map data) {
        var result = {};

        if (data.containsKey('token')) {
            result['token'] = data['token'];
        }

        if (data.containsKey('pk')) {
            result['pk'] = data['pk'];
        } else {
            switch (objectType) {
                case 'group':
                    result['pk'] = group_pk; break;
                case 'task':
                    result['pk'] = task_pk; break;
                case 'lineitem':
                    result['pk'] = lineitem_pk; break;
            }
        }

        for (var childType in ['group', 'task', 'lineitem']) {
            var childList = '${childType}s';
            if (data.containsKey(childList)) {
                result[childList] = [];
                for (var child in data[childList]) {
                    result[childList].add(response(childType, child));
                }
            }
        }

        return result;
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

    Future<Map> save(int jobId, Map data) {
        var request = new FakeRequest(data);
        _requests.add(request);
        return request.completer.future;
    }

}
