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

    bool addWorker(FieldWorker w) {
        if (!workers.contains(w)) {
            workers.add(w);
            update();
            return true;
        }
        return false;
    }

    removeWorker(FieldWorker w) {
        workers.remove(w);
        update();
    }

    bool addEquipment(FieldEquipment e) {
        if (!equipment.contains(e)) {
            equipment.add(e);
            update();
            return true;
        }
        return false;
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
            style.display = 'none';
        } else {
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
    SpanElement workers_header;
    DivElement workers_empty;
    SpanElement equipment_header;
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

}


class FieldItem extends HtmlElement {

    int get item_id => int.parse(this.dataset['id']);

    ButtonElement copy_button;
    StreamSubscription<Event> copy_event;

    String name;
    DailyPlan plan;

    FieldItem.created() : super.created(); attached() {
        name = this.querySelector('.name').text;
        plan = this.parent.parent;
        copy_button = this.querySelector(":scope .copy-button");
        copy_event = copy_button.onClick.listen(toggleCopy);
    }

    detached() {
        copy_event.cancel();
    }

    String toString() => name;

    toggleCopy([_]) {
        copy_button.classes.remove('active');
        if (addSelf()) {
            copy_button.classes.add('active');
        } else {
            removeSelf();
        }
    }

    cancelCopy() => copy_button.classes.remove('active');

    bool addSelf();
    removeSelf();
}


class FieldWorker extends FieldItem {
    FieldWorker.created() : super.created();
    bool addSelf() => clipboard.addWorker(this);
    removeSelf() => clipboard.removeWorker(this);
}


class FieldEquipment extends FieldItem {
    FieldEquipment.created() : super.created();
    bool addSelf() => clipboard.addEquipment(this);
    removeSelf() => clipboard.removeEquipment(this);
}


void main() {
    document.registerElement('field-clipboard', FieldClipboard);
    document.registerElement('daily-plan', DailyPlan);
    document.registerElement('field-worker', FieldWorker);
    document.registerElement('field-equipment', FieldEquipment);
    clipboard = querySelector('field-clipboard');
}
