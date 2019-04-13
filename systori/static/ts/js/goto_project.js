"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
class SystoriGotoProject extends HTMLElement {
    constructor() {
        super();
        this.infoBox = document.querySelector("#infoBox");
        this.queryPk = 0;
        this.projectFound = false;
        this.addEventListener('keyup', e => {
            this.handleKeyup(e);
        });
        this.addEventListener('keydown', e => {
            this.handleKeydown(e);
        });
    }
    showInfo(response, type) {
        this.infoBox.className = "input-group-addon";
        if (type == "success") {
            this.infoBox.classList.add("label-success");
            this.infoBox.innerText = `${response.name}`;
        }
        else if (type == "warning") {
            this.infoBox.classList.add("label-warning");
            this.infoBox.innerText = `${response.name}`;
        }
        else if (type == "reset") {
            this.infoBox.innerText = '#';
        }
    }
    fetchProject() {
        return __awaiter(this, void 0, void 0, function* () {
            let response = yield fetch(`${window.location.origin}/api/project/${this.queryPk}/exists/`, { credentials: 'include' });
            if (response.status == 200) {
                this.showInfo(yield response.json(), "success");
                this.projectFound = true;
            }
            else if (response.status == 206) {
                this.showInfo(yield response.json(), "warning");
                this.projectFound = false;
            }
        });
    }
    handleKeyup(event) {
        return __awaiter(this, void 0, void 0, function* () {
            this.queryPk = parseInt(event.target.innerText);
            if (isNaN(this.queryPk)) {
                this.showInfo("", "reset");
            }
            else {
                yield this.fetchProject();
            }
        });
    }
    handleKeydown(event) {
        if (event.key == "Enter" && this.projectFound == true) {
            event.preventDefault();
            window.location.href = `${window.location.origin}/project-${this.queryPk}`;
        }
        else if (event.key == "Enter") {
            event.preventDefault();
        }
    }
}
window.customElements.define("sys-goto-project", SystoriGotoProject);
//# sourceMappingURL=goto_project.js.map