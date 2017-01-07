import 'dart:async';
import 'package:systori/editor.dart';


class FakeToken extends Token {
    int _previous = 100;
    next() => ++_previous;
}


abstract class FakeRequest<T> {
    final Map data;
    final Completer<T> completer = new Completer.sync();
    FakeRequest(this.data);
    complete() => completer.complete(response(data));
    fail() => completer.completeError('failed');
    T response(Map data);
}


class FakeSaveRequest extends FakeRequest<Map> {

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

    FakeSaveRequest(Map data): super(data);

    Map response(Map data) => _response('job', data);

    Map _response(String objectType, Map data) {
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
                    result[childList].add(_response(childType, child));
                }
            }
        }

        return result;
    }

}


class FakeSearchRequest extends FakeRequest<List> {
    FakeSearchRequest(Map data): super(data);
    List<List> response(Map data) {
        print('responding from response');
        return [['42', 'a name', 'a description']];
    }
}


class FakeInjectRequest extends FakeRequest<String> {
    FakeInjectRequest(Map data): super(data);
    String response(Map data) => '';
}


class FakeRepository extends Repository {

    List<FakeRequest> _requests = [];

    FakeRequest get lastRequest =>
        _requests.last;

    Map get lastRequestMap =>
        lastRequest.data;

    FakeRepository() {
        FakeSaveRequest.reset();
    }

    fail() {
        _requests.forEach((request) => request.fail());
        _requests.clear();
    }

    complete() {
        print('complete():');
        print(_requests);
        _requests.forEach((request) => request.complete());
        _requests.clear();
    }

    FakeRequest pop() => _requests.removeLast();

    Future<Map> save(int jobId, Map data) {
        var request = new FakeSaveRequest(data);
        _requests.add(request);
        return request.completer.future;
    }

    Future<List<List>> search(Map<String,String> criteria) {
        var request = new FakeSearchRequest(criteria);
        _requests.add(request);
        return request.completer.future;
    }

    Future<String> inject(Map<String,String> params) {
        var request = new FakeInjectRequest(params);
        _requests.add(request);
        return request.completer.future;
    }

}
