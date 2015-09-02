import 'dart:html';
import 'dart:convert';
import 'package:intl/intl.dart';
import 'dart:async';
import 'package:intl/date_symbol_data_local.dart';


DateTime parseDate() {
    DateTime date = DateTime.parse(document.querySelector('#selected_date').attributes['data-date']);
    return date;
}

String getRFCDate(date) {
    var formatter = new DateFormat('yyyy-MM-dd');
    return Intl.withLocale('de_DE', () => formatter.format(date));
}

void setDisplayDate(List received_date) {
    SpanElement selected_date = document.querySelector('#selected_date');
    selected_date.innerHtml = received_date[1];
    setSelectedDate(DateTime.parse(received_date[0]));
}

void setSelectedDate(date) {
    SpanElement selected_date = document.querySelector('#selected_date');
    selected_date.attributes['data-date'] = getRFCDate(date);
}

void hide_spinner() {
    var spinner = document.querySelector('#loader');
    spinner.style.visibility = "hidden";
}

void loadData(DateTime date) {
    String rfc_date = getRFCDate(date);

    var url = "http://localhost:8000/dailyplans-json/${rfc_date}";

    var httpRequest = new HttpRequest();
    httpRequest
        ..open('GET', url)
        ..onLoadEnd.listen((e) => onDataLoaded(httpRequest))
        ..send('');
}

void onDataLoaded(HttpRequest request) {
    if (request.status == 200) {
        createElements(request.responseText);
        hide_spinner();
    }

}

void loadDailyPlan(int id) {
    var url = "http://localhost:8000/dailyplan-${id}";

    // call the web server asynchronously
    var request = HttpRequest.getString(url).then(onDailyPlanLoaded);
}

void onDailyPlanLoaded(String dailyPlan) {
    appendDailyPlan(dailyPlan);
}

void appendDailyPlan(String dailyplan) {
    Element dailyplan_container = document.querySelector('#dailyplan-container');
    dailyplan_container.append(stringToDocumentFragment(dailyplan));
}

void createElements(String data) {
    var dailyplan_container = document.querySelector('#dailyplan-container');
    List parsedData = JSON.decode(data);

    dailyplan_container.children.clear();

    if (parsedData.length != 0) {
        setDisplayDate(parsedData['selected_date']);

        parsedData['dailyplan_ids'].forEach((el) {
            loadDailyPlan(el);
        });
    } else {
        DivElement div = new DivElement();
        div.text = "Keine Daten verfügbar.";
        dailyplan_container.append(div);
    }
}

DocumentFragment stringToDocumentFragment(html) {
    var tmp = document.createDocumentFragment();
    tmp.setInnerHtml(html, validator:
    new NodeValidatorBuilder.common()
        ..allowElement('div', attributes: ['contenteditable', 'placeholder', 'data-pk'])
        ..allowElement('span', attributes: ['area-hidden'])
        ..allowElement('br')
        ..allowElement('table')
        ..allowElement('tbody')
        ..allowElement('tr')
        ..allowElement('td')
    );
    return tmp;
}

void setupEventHandlers() {
    ButtonElement next_day = document.querySelector('#next_day');
    ButtonElement previous_day = document.querySelector('#previous_day');
    var autorefresh = document.querySelector('#autorefresh');

    next_day.onClick.listen((MouseEvent e) => nextDay(e, parseDate()));
    previous_day.onClick.listen((MouseEvent e) => previousDay(e, parseDate()));
    autorefresh.onChange.listen((Event e) => setAutorefresh());
}

void nextDay(Event e, DateTime date) => loadData(date.add(new Duration(days:1)));

void previousDay(Event e, DateTime date) => loadData(date.subtract(new Duration(days:1)));

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
    initializeDateFormatting(Intl.systemLocale, null);
    DateTime date = parseDate();

    setupEventHandlers();
    loadData(date);
    setAutorefresh();
}
