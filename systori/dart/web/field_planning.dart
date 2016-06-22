import 'dart:html';
import 'dart:async';
import 'dart:convert';


final Repository repository = new Repository();


class Repository {

    Map<String, String> headers;

    Repository() {
        var csrftoken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
        headers = {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        };
    }

    Future<bool> paste(String url, List<int> workers, List<int> equipment) {
        var wait_for_response = HttpRequest.request(
                url,
                method: "POST",
                requestHeaders: headers,
                sendData: JSON.encode({
                    'workers': workers,
                    'equipment': equipment
                })
        );

        var result = new Completer<int>();
        wait_for_response.then((response) {
            if (response.status == 200) {
                result.complete(true);
            } else {
                result.completeError("Wrong status returned from server.");
            }
        }, onError: result.completeError);
        return result.future;
    }

}


FieldClipboard clipboard;


class FieldClipboard extends HtmlElement {

    List<FieldWorker> workers = [];
    List<FieldEquipment> equipment = [];
    DivElement content;

    FieldClipboard.created() : super.created(); attached() {
        content = this.querySelector('#clipboard');
        this.querySelector('#cancel-clipboard').onClick.listen(cancel);
    }

    addWorker(FieldWorker w) {
        workers.add(w);
        update();
    }

    removeWorker(FieldWorker w) {
        workers.remove(w);
        update();
    }

    addEquipment(FieldEquipment e) {
        equipment.add(e);
        update();
    }

    removeEquipment(FieldEquipment e) {
        equipment.remove(e);
        update();
    }

    update() {
        content.setInnerHtml(
            workers.join(', ') + '<br />' +
            equipment.join(', ')
        );
        if (equipment.isEmpty && workers.isEmpty) {
            querySelectorAll('daily-plan').forEach((DailyPlan dp) => dp.hidePasteButton());
            style.display = 'none';
        } else {
            querySelectorAll('daily-plan').forEach((DailyPlan dp) => dp.showPasteButton());
            style.display = 'block';
        }
    }

    cancel([_]) {
        workers.forEach((w) => w.cancelCopy());
        workers.clear();
        equipment.forEach((e) => e.cancelCopy());
        equipment.clear();
        update();
    }

    pasteTo(DailyPlan dp) {
        repository.paste(
            dp.paste_url,
            workers.map((w) => w.item_id).toList(),
            equipment.map((e) => e.item_id).toList()
        );
        var dailyplans = [dp];
        [workers, equipment].forEach((list) => list.forEach((FieldItem i) {
            !dailyplans.contains(i.plan) && dailyplans.add(i.plan);
        }));
        workers.forEach((w) => dp.addWorker(w));
        equipment.forEach((e) => dp.addEquipment(e));
        dailyplans.forEach((DailyPlan dp) => dp.updateEmptyMessage());
        cancel();
    }

}


class DailyPlan extends HtmlElement {

    ButtonElement paste_button;
    HtmlElement workers_header;
    DivElement workers_empty;
    HtmlElement equipment_header;
    DivElement equipment_empty;

    String paste_url;

    DailyPlan.created() : super.created(); attached() {
        paste_url = this.dataset['paste-url'];
        paste_button = this.querySelector(".paste-button");
        paste_button.onClick.listen(doPaste);
        workers_header = this.querySelector(".workers-header");
        workers_empty = this.querySelector(".workers-empty");
        equipment_header = this.querySelector(".equipment-header");
        equipment_empty = this.querySelector(".equipment-empty");
    }

    doPaste(_) =>
        clipboard.pasteTo(this);

    addWorker(FieldWorker fw) {
        workers_header.insertAdjacentElement('afterend', fw);
    }

    addEquipment(FieldEquipment fe) {
        equipment_header.insertAdjacentElement('afterend', fe);
    }

    updateEmptyMessage() {
        if (this.querySelector('field-worker') == null) {
            workers_empty.style.display = 'block';
        } else {
            workers_empty.style.display = 'none';
        }
        if (this.querySelector('field-equipment') == null) {
            equipment_empty.style.display = 'block';
        } else {
            equipment_empty.style.display = 'none';
        }
    }

    hidePasteButton() {
        paste_button.style.display = 'none';
    }

    showPasteButton() {
        var items = this.querySelectorAll('field-worker,field-equipment');
        var has_selected = items.any((FieldItem fi) => fi.selected);
        if (has_selected) {
            hidePasteButton();
        } else {
            paste_button.style.display = 'block';
        }
    }

}


class FieldItem extends HtmlElement {

    static String SELECTED = 'list-group-item-warning';

    StreamSubscription<Event> copy_event;

    int get item_id => int.parse(this.dataset['id']);
    String get name => this.text;
    DailyPlan get plan => this.parent.parent;
    bool get selected => this.classes.contains(SELECTED);

    FieldItem.created() : super.created(); attached() {
        copy_event = this.onClick.listen(toggleCopy);
    }

    detached() {
        copy_event.cancel();
    }

    String toString() => '<span class="badge">' + name + '</span>';

    toggleCopy([_]) {
        this.classes.remove(SELECTED);
        if (!containsSelf()) {
            this.classes.add(SELECTED);
            addSelf();
        } else {
            removeSelf();
        }
    }

    cancelCopy() => this.classes.remove(SELECTED);

    bool containsSelf();
    addSelf();
    removeSelf();
}


class FieldWorker extends FieldItem {
    FieldWorker.created() : super.created();
    bool containsSelf() => clipboard.workers.contains(this);
    addSelf() => clipboard.addWorker(this);
    removeSelf() => clipboard.removeWorker(this);
}


class FieldEquipment extends FieldItem {
    FieldEquipment.created() : super.created();
    bool containsSelf() => clipboard.equipment.contains(this);
    addSelf() => clipboard.addEquipment(this);
    removeSelf() => clipboard.removeEquipment(this);
}


void main() {
    document.registerElement('field-clipboard', FieldClipboard);
    document.registerElement('daily-plan', DailyPlan);
    document.registerElement('field-worker', FieldWorker);
    document.registerElement('field-equipment', FieldEquipment);
    clipboard = querySelector('field-clipboard');
}
