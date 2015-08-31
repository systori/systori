import 'dart:html';
import 'dart:convert';
import 'package:intl/intl.dart';
import 'dart:async';

void init() {
    DateTime date = new DateTime.now();

    setSelectDay(date);
    setupEventHandlers();
    loadData(date);
}

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
            div.classes.add('dailyplan');
            DivElement p = new DivElement();
            p.text = el['project'];
            p.classes.add('project');
            div.append(p);
            el['workers'].forEach((worker) {
                SpanElement s = new SpanElement();
                s.classes.addAll(['glyphicon','glyphicon-user']);
                s.attributes['area-hidden'] = 'true';
                DivElement w = new DivElement();
                w.append(s);
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
    switch (date.weekday) {
        case 1:
            display_weekday.innerHtml = translated_weekdays[0];
            display_weekday.style.color= "black";
            break;
        case 2:
            display_weekday.innerHtml = translated_weekdays[1];
            display_weekday.style.color= "black";
            break;
        case 3:
            display_weekday.innerHtml = translated_weekdays[2];
            display_weekday.style.color= "black";
            break;
        case 4:
            display_weekday.innerHtml = translated_weekdays[3];
            display_weekday.style.color= "black";
            break;
        case 5:
            display_weekday.innerHtml = translated_weekdays[4];
            display_weekday.style.color= "black";
            break;
        case 6:
            display_weekday.innerHtml = translated_weekdays[5];
            display_weekday.style.color= "red";
            break;
        case 7:
            display_weekday.innerHtml = translated_weekdays[6];
            display_weekday.style.color= "red";
            break;
    }

}

void checkDateTimeRelevance(DateTime date, Function fn) {
    // this function checks the DateTime object and jumps to the next day when the
    // conditions match. f.e. we don't need to display today but tomorrow if it's past 16 o'clock
    // applies to autorefresh only
    if (date.hour > 23 || date.weekday > 5) {
        fn(date.add(new Duration(days:1)));
    } else {
        fn(date);
    }
}

void setAutorefresh() {
    const fiveSec = const Duration(seconds:5);
    var loadDataCallback = ((Timer t) {
        if (!document.querySelector('#autorefresh').checked) t.cancel();
        DateTime date = new DateTime.now();
        checkDateTimeRelevance(date, loadData);
    });
    Timer timer = new Timer.periodic(fiveSec, (Timer t) => loadDataCallback(t));
}

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;
    init();
}
