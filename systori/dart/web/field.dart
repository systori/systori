import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;

    InputElement complete_range_slider = querySelector('#completion-range');
    InputElement complete_input = querySelector('input[name="complete"]');
    InputElement submit_button = querySelector('#task-submit');
    HtmlElement percent_label = querySelector('#percent');
    double complete_range_max = double.parse(complete_range_slider.attributes['max']);

    complete_range_slider.onInput.listen((e) {
        double range_position = double.parse(e.currentTarget.value);
        int percent_value = (range_position / complete_range_max * 100).round();
        percent_label.innerHtml = '$percent_value%';
        complete_input.value = CURRENCY.format(range_position);
    });

    complete_input.onKeyUp.listen((e) {
        String input = e.currentTarget.value;
        double parsed_input;
        if (input == '') {
            percent_label.innerHtml = '0%';
            complete_range_slider.value = CURRENCY.format(0);
        } else {
            try {
                parsed_input = parse_decimal(input);
            } catch(e) {
                complete_input.parent.classes.add('has-error');
                submit_button.attributes['disabled'] = 'disabled';
                return;
            }
            complete_input.parent.classes.remove('has-error');
            submit_button.attributes.remove('disabled');
            int percent_value = (parsed_input / complete_range_max * 100).round();
            percent_label.innerHtml = '$percent_value%';
            complete_range_slider.value = parsed_input.round().toString();
        }
    });
}
