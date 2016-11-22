import 'dart:html';
import 'dart:async';
import 'dart:convert';
import 'editor.dart';
import 'model.dart';


class Repository {

    Future<Map> save(Model model) {

    }

    Future<bool> delete(Model model) {

    }

}


class ChangeManager {

    /*
    When a child of a new create is modified,
    find the parent and mark all ancestors as dirty.
    When the parent is finally being saved it will
    only save children marked as dirty.
    This prevents the case where use is hitting
    enter and getting throw away groups/tasks,
    we don't want to save those.
     */

    Timer timer;
    Repository repository;
    Set<Model> save = new Set();
    Set<Model> saving = new Set();
    Set<Model> delete = new Set();
    Set<Model> deleting = new Set();

    ChangeManager(this.repository);

    startAutoSync() =>
        timer = new Timer.periodic(new Duration(milliseconds: 5), (_)=>sync());

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
                saving.add(model);
                repository.save(model).then((map)=>saved(map, model));
            }
        }
        save = stillPending;
    }

    saved(Map result, Model model) {
        model.state.commit();
        saving.remove(model);
    }

    changed(Model model) => save.add(model);
    deleted(Model model) => delete.add(model);

}
