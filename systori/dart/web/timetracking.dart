import 'dart:html';
import 'dart:async';
import 'dart:convert';


final TimetrackingTimer timetracking_timer = new TimetrackingTimer();


class Resource {

    Map<String, String> headers;
    String url;
    int id;

    Resource(url): url = url {
        var csrftoken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
        headers = {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        };
    }

    String build_request_url() {
        if (id != null) {
          return "${url}${id}";
        } else {
          return url;
        }
    }

    Future<HttpRequest> create([Map data]) {
        return HttpRequest.request(
            url,
            method: "POST",
            requestHeaders: headers,
            sendData: JSON.encode(data)
        );
    }

    Future<HttpRequest> destroy() {
        return HttpRequest.request(
            build_request_url(),
            method: "DELETE",
            requestHeaders: headers
        );
    }

    Future<HttpRequest> get() {
        return HttpRequest.request(
            build_request_url(),
            method: "GET"
        );
    }

    Future<HttpRequest> update([Map data]) {
        return HttpRequest.request(
            build_request_url(),
            method: "PUT",
            requestHeaders: headers,
            sendData: JSON.encode(data)
        );
    }
}


class TimetrackingTimer extends Resource {

    InputElement box = querySelector('#timer-box');
    HtmlElement button;
    String _current_button_icon = 'play';
    HtmlElement _button_icon;
    HtmlElement _button_label;
    int hours = 0;
    int minutes = 0;
    int seconds = 0;
    Timer timer;

    TimetrackingTimer(): super("/api/v1/timetracking/timer/");

    void initialize() {
        button = querySelector('#timer-toggle');
        _button_icon = button.querySelector('.glyphicon');
        _button_label = button.querySelector('.btn-label');

        button.onClick.listen((_) {
            this.toggle();
        });

        get().then((response) {
            Map remote_data = JSON.decode(response.responseText);
            hours = remote_data['duration'][0];
            minutes = remote_data['duration'][1];
            seconds = remote_data['duration'][2];
            run();
        }).catchError((Error error) {
            output();
        });
    }

    Future<Map> _get_location() async {
        var data = new Map();
        try {
            Geoposition position = await window.navigator.geolocation.getCurrentPosition();
            data['latitude'] = position.coords.latitude.toStringAsFixed(8);
            data['longitude'] = position.coords.longitude.toStringAsFixed(8);
        } on PositionError catch (error) {
            if (window.navigator.userAgent.contains(new RegExp(r"(Chromium)|(Dart)"))) {
                // Dummy data for Chromium that doesn't support geolocation
                data['latitude'] = 52.5076;
                data['longitude'] = 131.39043904;
            }
            else {
                window.alert("Geolocation error: ${error.message} (${error.code})");
            }
        }
        return data;
    }

    void start() {
        set_button_icon('map-marker');
        set_button_label('geolocating');
        _get_location().then((data) {
            if (data.isNotEmpty) {
                var remote_data = {'start_latitude': data['latitude'], 'start_longitude': data['longitude']};
                create(remote_data).then((response) {
                    if (response.status == 200) {
                        run();
                    }
                });
            } else {
                set_button_icon('play');
                set_button_label('stopped');
            }
        });
    }

    void toggle() {
        isRunning() ? stop() : start();
    }

    void run() {
        timer = new Timer.periodic(new Duration(milliseconds: 1000), increment);
        set_button_icon('pause');
        set_button_label('running');
    }

    void increment(Timer timer) {
        seconds += 1;
        if (seconds >= 60) {
            seconds = 0;
            minutes += 1;
        }
        if (minutes >= 60) {
            minutes = 0;
            hours += 1;
        }
        output();
    }

    void output() {
        var hours_string = "${hours}".padLeft(2, "0");
        var minutes_string = "${minutes}".padLeft(2, "0");
        var seconds_string = "${seconds}".padLeft(2, "0");
        box.text = "${hours_string}:${minutes_string}:${seconds_string}";
    }

    void stop() {
        set_button_icon('map-marker');
        set_button_label('geolocating');
        _get_location().then((data) {
            var remote_data = {'end_latitude': data['latitude'], 'end_longitude': data['longitude']};
            update(remote_data).then((response) {
                if (response.status == 200) {
                    set_button_icon('play');
                    set_button_label('stopped');
                }
            });
        });
        timer.cancel();
        hours = minutes = seconds = 0;
        output();
    }

    bool isRunning() {
        return timer == null ? false : timer.isActive;
    }

    void set_button_icon(String name) {
        _button_icon.classes.remove('glyphicon-${_current_button_icon}');
        _current_button_icon = name;
        _button_icon.classes.add('glyphicon-${_current_button_icon}');
    }

    void set_button_label(String string_constant) {
        _button_label.text = _button_label.dataset["label-${string_constant}"];
    }
}


void main() {
    timetracking_timer.initialize();
}
