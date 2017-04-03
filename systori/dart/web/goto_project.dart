import 'dart:html';
import 'package:systori/src/inputs/input.dart';


class SystoriGotoProjectInput extends TextInput with KeyboardHandler {
    factory SystoriGotoProjectInput() => new Element.tag(tag);

    static final tag = 'sys-goto-project';
    static final project_url = window.location.origin+"/project-";
    bool exists = false;
    int project_id;

    SystoriGotoProjectInput.created() : super.created() {
        addKeyHandler(this);
    }

    void checkProjectExists(project_id) {
        String url = window.location.origin+"/api/project-available/"+project_id.toString();
        HttpRequest.getString(url).then(parseResponse);
    }

    void parseResponse(String responseText) {
        if (responseText == 'true') {
            exists = true;
        } else {
            exists = false;
            this.style.color = "red";
        }
    }

    @override
    onKeyUpEvent(KeyEvent e, TextInput input) {
        input.style.color = "initial";
        try {
            project_id = int.parse(input.text);
            checkProjectExists(project_id);
        } catch(_) {
            project_id = 0;
            input.style.color = "red";
        }
    }

    @override
    onKeyDownEvent(KeyEvent e, TextInput input) {
        if (e.keyCode == KeyCode.ENTER) {
            e.preventDefault();
            if (project_id != 0 && exists) {
                window.location.href = project_url + project_id.toString();
            }
        }
    }

}


void main() {
    document.registerElement('sys-goto-project', SystoriGotoProjectInput);
}