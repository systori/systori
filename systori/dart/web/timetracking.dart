import 'dart:html';
import 'dart:async';
import 'dart:convert';

// final Resource resource = new Resource();
final TimetrackingTimer timetracking_timer = new TimetrackingTimer();


class Resource {

    Map<String, String> headers;
    String url;
    int id;

    Resource() {
        var csrftoken = (querySelector('input[name=csrfmiddlewaretoken]') as InputElement).value;
        headers = {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        };
    }

    String build_request_url() =>
        id ? "${url}${id}" : url;

    Future<int> create([Map data]) {
        return HttpRequest.request(
                url,
                method: "POST",
                requestHeaders: headers,
                sendData: JSON.encode(data)
        );
    }

    Future<int> destroy() {
        return HttpRequest.request(
                build_request_url(),
                method: "DELETE",
                requestHeaders: headers
        );
    }

    Future<int> get() {
        return HttpRequest.request(
                build_request_url(),
                method: "GET"
        );
    }

    Future<int> update([Map data]) {
        return HttpRequest.request(
                build_request_url(),
                method: "PUT",
                requestHeaders: headers,
                sendData: JSON.encode(data)
        );
    }
}


class TimetrackingTimer extends Resource {
    String url = "/api/v1/timetracking/timer/";
    InputElement timer_box = querySelector('#timer-box');
    int hours = 0;
    int minutes = 0;
    int seconds = 0;
    Timer timer;

    void initialize() {
        get().then((response) {
            Map data = JSON.decode(response.responseText);
            hours = data['duration'][0];
            minutes = data['duration'][1];
            seconds = data['duration'][2];
            run();
        }).catchError((Error error) {
            output();
        });
    }

    void start() {
        create().then((response) {
            if (response.status == 200) {
                run();
            }
        });
    }

    void toggle() {
        isRunning() ? stop() : start();
    }

    void run() {
        timer = new Timer.periodic(new Duration(milliseconds: 1000), increment);
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
        timer_box.text = "${hours_string}:${minutes_string}:${seconds_string}";
    }

    void stop() {
        update();
        timer.cancel();
        hours = minutes = seconds = 0;
        output();
    }

    bool isRunning() {
        return timer == null ? false : timer.isActive;
    }
}


setup_buttons() {
    querySelector('#timer-toggle').onClick.listen((_) => timetracking_timer.toggle());
}


void main() {
    setup_buttons();
    timetracking_timer.initialize();
}