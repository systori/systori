import 'dart:html';
import 'package:intl/intl.dart';
import 'package:systori/numbers.dart';


void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;

    InputElement complete_range_slider = querySelector('#completion-range');
    InputElement complete_input = querySelector('input[name="complete"]');
    InputElement submit_button = querySelector('#task-submit');
    HtmlElement percent_label = querySelector('#percent');
    Decimal complete_range_max = new Decimal.parse(complete_range_slider.attributes['max']);

    complete_range_slider.onInput.listen((e) {
        Decimal range_position = new Decimal.parse(complete_range_slider.value);
        percent_label.innerHtml = (range_position / complete_range_max).percent;
        complete_input.value = range_position.money;
    });

    complete_input.onKeyUp.listen((e) {
        String input = complete_input.value;
        Decimal parsed_input;
        if (input == '') {
            percent_label.innerHtml = '0%';
            complete_range_slider.value = new Decimal(0).money;
        } else {
            try {
                parsed_input = new Decimal.parse(input);
            } catch(e) {
                complete_input.parent.classes.add('has-error');
                submit_button.attributes['disabled'] = 'disabled';
                return;
            }
            complete_input.parent.classes.remove('has-error');
            submit_button.attributes.remove('disabled');
            percent_label.innerHtml = (parsed_input / complete_range_max).percent;
            complete_range_slider.value = parsed_input.decimal.round().toString();
        }
    });
}
