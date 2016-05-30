import 'dart:html';

void main() {
    HtmlElement report_table = querySelector('#timetracking-report');
    NodeList enter_buttons = report_table.querySelectorAll('.timetracking-enter-toggle');
    enter_buttons.onClick.listen((MouseEvent event) {
        int user_id = event.target.parent.dataset['user-rel'];
        HtmlElement form_box = report_table.querySelector(
            '.timetracking-enter-form[data-user-rel="${user_id}"]');
        form_box.classes.toggle('hidden-box');
    });
}