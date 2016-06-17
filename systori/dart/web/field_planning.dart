import 'dart:html';
import 'dart:async';

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
        workers.forEach((w) => dp.addWorker(w));
        equipment.forEach((e) => dp.addEquipment(e));
        cancel();
    }

}


class DailyPlan extends HtmlElement {

    ButtonElement paste_button;
    SpanElement workers_header;
    SpanElement equipment_header;

    DailyPlan.created() : super.created(); attached() {
        paste_button = this.querySelector(":scope .paste-button");
        paste_button.onClick.listen(doPaste);
        workers_header = this.querySelector(":scope .workers-header");
        equipment_header = this.querySelector(":scope .equipment-header");
    }

    doPaste(_) =>
        clipboard.pasteTo(this);

    addWorker(FieldWorker fw) =>
        workers_header.insertAdjacentElement('afterend', fw);

    addEquipment(FieldEquipment fe) =>
        equipment_header.insertAdjacentElement('afterend', fe);

}


class FieldItem extends HtmlElement {

    ButtonElement copy_button;
    StreamSubscription<Event> copy_event;

    String name;

    FieldItem.created() : super.created(); attached() {
        name = this.querySelector('.name').text;
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
