import 'dart:html';
import 'dart:convert';
import 'package:systori/src/inputs/input.dart';


class SystoriGotoProjectInput extends TextInput with KeyboardHandler {
    factory SystoriGotoProjectInput() => new Element.tag(tag);

    static final tag = 'sys-goto-project';
    static final project_url = window.location.origin+"/project-";
    bool exists = false;
    int project_id;
    String errorResponse;

    SystoriGotoProjectInput.created() : super.created() {
        addKeyHandler(this);
    }

    void checkProjectExists(project_id) {
        String url = window.location.origin+"/api/project-available/"+project_id.toString();
        HttpRequest.getString(url).then(parseResponse).catchError((Error error) {
            errorResponse = JSON.decode(error.target.responseText)["detail"];
            showError(errorResponse);
        });
    }

    void showError(String errorResponse) {
        DivElement errorTooltip = document.createElement('div');
        errorTooltip.style.position = "absolute";
        errorTooltip.style.top = "${this.parent.offsetTop + 30} px";
        errorTooltip.style.left = "${this.parent.offsetLeft} px";
        errorTooltip.style.background = "#D41351";
        errorTooltip.style.width = "150px";
        errorTooltip.style.padding = "5px";
        errorTooltip.text = "${errorResponse}";
        this.parent.children.add(errorTooltip);
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
            if (errorResponse != null) {
                showError(errorResponse);
            } else {
                project_id = int.parse(input.text);
                checkProjectExists(project_id);
            }
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