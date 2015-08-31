import 'dart:html';
import 'dart:convert';
import 'package:intl/intl.dart';
import 'dart:async';


void setSelectDay(date) {
    InputElement select_day = document.querySelector('#select_day');
    select_day.value = "${date.year.toString()}-${date.month.toString().padLeft(2,'0')}-${date.day.toString().padLeft(2,'0')}";
    setDisplayWeekday(date);
}

void hide_spinner() {
    var spinner = document.querySelector('#loader');
    spinner.style.visibility = "hidden";
}

void loadData(DateTime date) {
    setSelectDay(date);
    String date_formatted =
        "${date.year.toString()}-${date.month.toString().padLeft(2,'0')}-${date.day.toString().padLeft(2,'0')}";

    var url = "http://localhost:8000/dailyplans-json/${date_formatted}";

    // call the web server asynchronously
    var request = HttpRequest.getString(url).then(onDataLoaded);
}

void onDataLoaded(String responseText) {
    String jsonString = responseText;
    createElements(jsonString);
    hide_spinner();
}

void createElements(String data) {
    var dailyplan_container = document.querySelector('#dailyplan-container');
    List parsedData = JSON.decode(data);

    dailyplan_container.children.clear();

    if (parsedData.length != 0) {
        parsedData.forEach((el) {
            DivElement div = new DivElement();
            SpanElement icon_flag = new SpanElement();
            icon_flag.classes.addAll(['glyphicon','glyphicon-flag']);
            icon_flag.attributes['area-hidden'] = 'true';
            div.classes.add('dailyplan');
            DivElement p = new DivElement();
            p.append(icon_flag);
            p.appendText(el['project']);
            p.classes.add('project');
            div.append(p);
            SpanElement icon_worker = new SpanElement();
            icon_worker.classes.addAll(['glyphicon','glyphicon-user']);
            icon_worker.attributes['area-hidden'] = 'true';
            div.append(icon_worker);
            el['workers'].forEach((worker) {
                DivElement w = new DivElement();
                w.appendText("${worker[0]} ${worker[1]}");
                w.classes.add('worker');
                div.append(w);
            });
            dailyplan_container.append(div);
        });
    } else {
        DivElement div = new DivElement();
        div.text = "Keine Daten verfügbar.";
        dailyplan_container.append(div);
    }
}

void setupEventHandlers() {
    InputElement select_day = document.querySelector('#select_day');
    ButtonElement next_day = document.querySelector('#next_day');
    ButtonElement previous_day = document.querySelector('#previous_day');
    var autorefresh = document.querySelector('#autorefresh');

    select_day.onChange.listen((MouseEvent e) => selectDay(e));
    next_day.onClick.listen((MouseEvent e) => nextDay(e, DateTime.parse(select_day.value)));
    previous_day.onClick.listen((MouseEvent e) => previousDay(e, DateTime.parse(select_day.value)));
    autorefresh.onChange.listen((Event e) => setAutorefresh());
}


void nextDay(Event e, DateTime date) => loadData(date.add(new Duration(days:1)));

void previousDay(Event e, DateTime date) => loadData(date.subtract(new Duration(days:1)));

void selectDay(Event e) {
    //Dartium crashes.
}
void setDisplayWeekday(DateTime date) {
    HtmlElement display_weekday = document.querySelector('#weekday');
    List<String> translated_weekdays = [];
    List<String> weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"];
    for (String weekday in weekdays) {
        translated_weekdays.add(document.querySelector('#$weekday').text);
    };
    var colors = ['black', 'black', 'black', 'black', 'black', 'red', 'red'];
    display_weekday.innerHtml = translated_weekdays[date.weekday - 1];
    display_weekday.style.color = colors[date.weekday - 1];

}

bool checkDateTimeRelevance(DateTime date) {
    // this function checks the DateTime object and jumps to the next day when the
    // conditions match. f.e. we don't need to display today but tomorrow if it's past 15 o'clock
    // applies to autorefresh only
    if (date.hour > 15 || date.weekday > 5) {
        return true;
    } else {
        return false;
    }
}

void setAutorefresh() {
    const fiveSec = const Duration(seconds:5);
    new Timer.periodic(fiveSec, (Timer t) {
        if (!document.querySelector('#autorefresh').checked) {
            t.cancel();
            return;
        }
        DateTime date = new DateTime.now();
        if(checkDateTimeRelevance(date)){
            loadData(date.add(new Duration(days:1)));
        } else {
            loadData(date);
        }
    });
}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    DateTime date = new DateTime.now();

    setSelectDay(date);
    setupEventHandlers();
    loadData(date);
}
