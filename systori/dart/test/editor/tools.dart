import 'dart:async';
import 'dart:html';
import 'package:systori/editor.dart';
import 'package:systori/inputs.dart';
import '../keyboard.dart';
export '../scaffolding.dart';


class KeyboardNavigator extends Keyboard {

    Model get activeModel {
        var e = document.activeElement;
        while (e != null) {
            if (e is Model) return e;
            e = e.parent;
        }
        return null;
    }

    String get inputName => (document.activeElement as Input).name;

}


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
    List<Map> response(Map data) => [{
        'id': '42',
        'name_match': 'a name',
        'description_match': 'a description'
    }];
}


class FakeInfoRequest extends FakeRequest<Map> {
    FakeInfoRequest(Map data): super(data);
    Map response(Map data) => {
        'id': '42',
        'name': 'a name',
        'description': 'a description'
    };
}


class FakeCloneRequest extends FakeRequest<String> {
    FakeCloneRequest(Map data): super(data);
    String response(Map data) {
        Group group = document.createElement('sys-group');
        group.pk = 99;
        return group.outerHtml;
    }
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

    fail() async {
        await new Future.value();
        for (var request in _requests) {
            request.fail();
        }
        _requests.clear();
    }

    complete() async {
        await new Future.value();
        for (var request in _requests) {
            request.complete();
        }
        _requests.clear();
    }

    FakeRequest pop() => _requests.removeLast();

    Future<Map> save(int jobId, Map data) {
        var request = new FakeSaveRequest(data);
        _requests.add(request);
        return request.completer.future;
    }

    Future<Map> info(String model, String id) {
        var request = new FakeInfoRequest({'model': model, 'id': id});
        _requests.add(request);
        return request.completer.future;
    }

    Future<List<Map>> search(Map<String,String> criteria) {
        var request = new FakeSearchRequest(criteria);
        _requests.add(request);
        return request.completer.future;
    }

    Future<String> clone(Map<String,String> params) {
        var request = new FakeCloneRequest(params);
        _requests.add(request);
        return request.completer.future;
    }

}
