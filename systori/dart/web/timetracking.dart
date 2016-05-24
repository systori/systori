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
    InputElement box = querySelector('#timer-box');
    HtmlElement button;
    ReportTable report_table;
    int hours = 0;
    int minutes = 0;
    int seconds = 0;
    Timer timer;

    void initialize() {
        report_table = document.querySelector('#timer-report');
        button = querySelector('#timer-toggle');
        button.onClick.listen((_) {
            this.toggle();
        });

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
                report_table.refresh();
            }
        });
    }

    void toggle() {
        isRunning() ? stop() : start();
    }

    void run() {
        timer = new Timer.periodic(new Duration(milliseconds: 1000), increment);
        button.children.first.classes.toggle('glyphicon-play');
        button.children.first.classes.toggle('glyphicon-pause');
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
        update().then((_) => report_table.refresh());
        timer.cancel();
        hours = minutes = seconds = 0;
        output();
        button.children.first.classes.toggle('glyphicon-play');
        button.children.first.classes.toggle('glyphicon-pause');
    }

    bool isRunning() {
        return timer == null ? false : timer.isActive;
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

    V operator[](Object key) => mapping[key].text;
    void operator []=(K key, V value) {
        mapping[key].text = value;
    }

    void fill(Map data) {
        mapping.forEach((key, value) {
            this[key] = data.containsKey(key) ? data[key] : '(None)';
        });
    }
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