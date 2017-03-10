import 'dart:html';
import 'dart:async';
import 'dart:convert';


class TimerAPI {

    static final String url = "/api/timer/";
    final Map<String, String> headers;

    TimerAPI(): headers = {
        "X-CSRFToken": (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value,
        "Content-Type": "application/json"
    };

    Future<bool> start(bool start, [Map data]) async {
        try {
            var response = await HttpRequest.request(
                url,
                method: start ? "POST" : "PUT",
                requestHeaders: headers,
                sendData: JSON.encode(data)
            );
            return response.status == 200 ? true : false;
        } catch(e) {
            return false;
        }
    }

}


Future<Map> geoLocate() async {
    try {
        Geoposition position = await window.navigator.geolocation.getCurrentPosition();
        return {
            'latitude': position.coords.latitude.toStringAsFixed(8),
            'longitude': position.coords.longitude.toStringAsFixed(8),
        };
    } catch(e) {
        return {};
    }
}


class TimerWidget extends HtmlElement {

    static final bool DEBUG = true;

    DateTime started;
    Timer ticker;
    TimerAPI api;

    DivElement digits;
    ButtonElement toggle;
    SpanElement toggleIcon;
    SpanElement toggleLabel;

    TimerWidget.created(): super.created() {
        api = new TimerAPI();
        digits = this.querySelector('#timer-digits');
        toggle = this.querySelector('#timer-toggle');
        toggle.onClick.listen(toggleState);
        toggleIcon = toggle.querySelector('.glyphicon');
        toggleLabel = toggle.querySelector('.btn-label');
        if (dataset['running'] == 'true') {
            var elapsed = new Duration(seconds: int.parse(dataset['seconds']));
            started = new DateTime.now().subtract(elapsed);
            startTicker();
        }
    }

    toggleState(_) =>
        started != null ? stop() : start();

    start() async {
        toggle.disabled = true;
        toggleLabel.text = toggleLabel.dataset['geolocating'];
        var location = await geoLocate();
        if (location.isEmpty) {
            toggleLabel.text = toggleLabel.dataset['geolocating-failed'];
        } else if (await api.start(true, location)) {
            started = new DateTime.now();
            toggleIcon.classes.add('glyphicon-pause');
            toggleIcon.classes.remove('glyphicon-play');
            toggleLabel.text = toggleLabel.dataset['started'];
            tick();
            startTicker();
        } else {
            toggleLabel.text = toggleLabel.dataset['start-failed'];
        }
        toggle.disabled = false;
    }

    stop() async {
        toggle.disabled = true;
        toggleLabel.text = toggleLabel.dataset['geolocating'];
        var location = await geoLocate();
        if (location.isEmpty) {
            toggleLabel.text = toggleLabel.dataset['geolocating-failed'];
        } else if (await api.start(false, location)) {
            ticker.cancel();
            started = null;
            toggleIcon.classes.add('glyphicon-play');
            toggleIcon.classes.remove('glyphicon-pause');
            toggleLabel.text = toggleLabel.dataset['stopped'];
            tick();
        } else {
            toggleLabel.text = toggleLabel.dataset['stop-failed'];
        }
        toggle.disabled = false;
    }

    startTicker() =>
        ticker = new Timer.periodic(new Duration(seconds: 1), tick);

    tick([_]) {
        if (started == null) {
            digits.text = '-:--';
        } else {
            var elapsed = new DateTime.now().difference(started);
            var hours = elapsed.inHours.toString();
            var minutes = (elapsed.inMinutes % 60).toString().padLeft(2, '0');
            if (DEBUG) {
                var seconds = (elapsed.inSeconds % 60).toString().padLeft(2, '0');
                digits.text = "$hours:$minutes:$seconds";
            } else {
                digits.text = "$hours:$minutes";
            }
        }
    }

}


class TimerAdminForm extends FormElement {

    SelectElement kind;
    CheckboxInputElement morningBreak;
    CheckboxInputElement lunchBreak;

    TimerAdminForm.created(): super.created() {
        kind = this.querySelector('select[name="kind"]');
        morningBreak = this.querySelector('input[name="morning_break"]');
        lunchBreak = this.querySelector('input[name="lunch_break"]');
        kind.onChange.listen(updateBreaks);
    }

    updateBreaks(Event e) {
        var selected = kind.options[kind.selectedIndex].value;
        switch(selected) {
            case 'work':
                morningBreak.disabled = lunchBreak.disabled = false;
                morningBreak.checked = lunchBreak.checked = true;
                return;
            default:
                morningBreak.disabled = lunchBreak.disabled = true;
                morningBreak.checked = lunchBreak.checked = false;
        }
    }

}


main() {
    document.registerElement('timer-form', TimerAdminForm, extendsTag:'form');
    document.registerElement('timer-widget', TimerWidget);
}
