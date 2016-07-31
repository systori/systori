import 'dart:html';
import 'package:intl/intl.dart';
import 'dart:async';
import 'dart:convert';
import 'dart:collection';


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
    String url = "/api/v1/timetracking/timer/";
    InputElement box = querySelector('#timer-box');
    HtmlElement button;
    String _current_button_icon = 'play';
    HtmlElement _button_icon;
    HtmlElement _button_label;
    ReportTable report_table;
    int hours = 0;
    int minutes = 0;
    int seconds = 0;
    Timer timer;

    void initialize() {
        report_table = document.querySelector('#timer-report');

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
                data['longitude'] = 13.3904;
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
            var remote_data = {'start_latitude': data['latitude'], 'start_longitude': data['longitude']};
            create(remote_data).then((response) {
                if (response.status == 200) {
                    run();
                    report_table.refresh();
                }
            });
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
                    report_table.refresh();
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


class Report extends Resource {
    String url = "/api/v1/timetracking/report/";
}


class ReportTableRow extends TableRowElement with MapMixin {
    Map<String, TableCellElement> mapping;

    ReportTableRow.created() : super.created(); attached() {
        mapping = new Map<String, TableCellElement>();
        this.children.forEach((TableCellElement cell) {
            var cell_name = cell.dataset['mapping'];
            mapping[cell_name] = cell;
            cell.classes.add('cell-${cell_name}');
        });
    }

    operator[](Object key) => mapping[key].text;

    void operator []=(Object key, String value) {
        mapping[key].text = value;
    }

    void fill(Map data) {
        mapping.forEach((key, value) {
            this[key] = data.containsKey(key) ? data[key] : '(None)';
        });
    }

    void clear() {}
}


class ReportTable extends TableElement {
    List data;
    var resource;
    TemplateElement template;
    TableElement body;

    ReportTable.created() : super.created(); attached() {
        body = this.querySelector('tbody');
        template = document.importNode(
            document.querySelector('template[for="timetracking-report-row"]').content, true);
        resource = new Report();
    }

    void refresh() {
        resource.get().then((response) {
            data = JSON.decode(response.responseText);
            refill(data);
        }).catchError((Error error) {
            // don't know what to output yet
        });
    }

    void insertReportRow() {
        body.append(template);
    }

    void deleteReportRow() {
        body.deleteRow(-1);
    }

    void allocateRows(int number) {
        var row_count = this.body.children.length - 1;
        new Iterable.generate(row_count - number).forEach((_) {
            this.deleteReportRow();
        });
        new Iterable.generate(number - row_count).forEach((_) {
            this.insertReportRow();
        });
    }

    void refill(List data) {
        this.allocateRows(data.length);
        var data_pivot = data.iterator;
        data_pivot.moveNext();
        // Skipping table head
        this.body.children.skip(1).forEach((row) {
            row.fill(data_pivot.current);
            data_pivot.moveNext();
        });
    }
}


void registerElements() {
    document.registerElement('timetracking-report', ReportTable, extendsTag:'table');
    document.registerElement('timetracking-report-row', ReportTableRow, extendsTag:'tr');
}


void main() {
    registerElements();
    timetracking_timer.initialize();
}
