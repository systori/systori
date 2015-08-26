import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;

    InputElement complete_range_slider = querySelector('#completion-range');
    InputElement complete_input = querySelector('input[name="complete"]');
    HtmlElement percent_label = querySelector('#percent');
    double complete_range_max = double.parse(complete_range_slider.attributes['max']);

    complete_range_slider.onInput.listen((e) {
        double range_position = double.parse(e.currentTarget.value);
        int percent_value = (range_position / complete_range_max * 100).round();
        percent_label.innerHtml = '$percent_value%';
    });

    complete_input.onKeyUp.listen((e) {
        String input = e.currentTarget.value;
        if (input == '') {
            percent_label.innerHtml = '0%';
            complete_range_slider.value = '0';
        } else {
            double parsed_input = parse_decimal(input);
            int percent_value = (parsed_input / complete_range_max * 100).round();
            percent_label.innerHtml = '$percent_value%';
            complete_range_slider.value = parsed_input.round().toString();
        }
    });
}
